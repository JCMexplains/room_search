import csv
import sys
import os

# Add the parent directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from ..my_rooms import MY_ROOMS
import pandas as pd

def lowercase_csv(input_file, output_file):
    with open(input_file, 'r') as infile, open(output_file, 'w', newline='') as outfile:
        reader = csv.reader(infile)
        writer = csv.writer(outfile)
        
        for row in reader:
            lowercase_row = [cell.lower() if isinstance(cell, str) else cell for cell in row]
            writer.writerow(lowercase_row)

def test_my_rooms(csv_file_path):
    """
    Read data from csv_file and print rows that match rooms in MY_ROOMS.
    
    :param csv_file_path: Path to the CSV file
    """
    # Create a new lowercase CSV file
    lowercase_csv_path = csv_file_path.rsplit('.', 1)[0] + '_lowercase.csv'
    lowercase_csv(csv_file_path, lowercase_csv_path)
    
    # Now use the lowercase CSV file
    df = pd.read_csv(lowercase_csv_path)
    
    # print("Debug: MY_ROOMS contents:")
    # for room in MY_ROOMS:
    #     print(f"Building: {room[0]}, Room: {room[1]}")

    print("\nRows matching rooms in MY_ROOMS:")
    # Lowercase all column names
    df.columns = df.columns.str.lower()
    
    # Lowercase all string values in the DataFrame
    df = df.applymap(lambda x: x.lower() if isinstance(x, str) else x)
    
    for index, row in df.iterrows():
        # Now use lowercase column names
        building = int(row['building'])
        room = row['room_number']
        
        # print(f"Debug: Raw row data: {row}")
        try:
            # print(f"Checking: Building {building}, Room {room}")
            
            if (building, room) in MY_ROOMS:
                print(f"Match found: Building {building}, Room {room}")
        except ValueError:
            print(f"Warning: Unable to convert Building or Room to int: {row['building']}, {row['roomnumber']}")

    # print("\nDebug: MY_ROOMS contents (for reference):")
    # for room in MY_ROOMS:
    #     print(f"Building: {room[0]}, Room: {room[1]}")

    print("\nUnique Building-Room combinations in CSV:")
    unique_combinations = set()
    df = pd.read_csv(csv_file_path)
    
    for index, row in df.iterrows():
        building = row['building'].strip()
        room = row['room_number'].strip()
        unique_combinations.add((building, room))
    for combo in sorted(unique_combinations):
        print(f"Building: {combo[0]}, Room: {combo[1]}")

if __name__ == "__main__":
    csv_file_path = 'C:/Users/james/Desktop/finding unused rooms/data.csv'
    test_my_rooms(csv_file_path)