# Open-CS100
A Better One without nonsense.

## Tool Description

This project contains a student ID hash conversion tool for converting hashed IDs in grade files back to real student IDs.

### hash_to_student_id.py

This is a Python script designed to convert hashed student IDs in CS100 course grade files back to real student IDs. The tool uses the FNV-1a hash algorithm to generate student ID mapping tables and supports batch conversion of student IDs across multiple years.

## Features

- 🔄 **Hash ID Conversion**: Convert hashed IDs in grade files to real student IDs
- 📅 **Multi-year Support**: Support for generating student ID mappings within specified year ranges
- 🎯 **High Coverage**: Includes extensive major codes to improve conversion success rate
- 📊 **Progress Display**: Real-time display of conversion progress and statistics
- 💾 **Result Saving**: Automatically save conversion results to new CSV files

## Installation Requirements

Ensure your system has Python 3.6+ installed and install the following dependencies:

```bash
pip install pandas tqdm
```

## Usage

### Basic Usage

```bash
python3 hash_to_student_id.py <input_file> [output_file]
```

### Detailed Parameters

```bash
python3 hash_to_student_id.py [-h] [-i INPUT] [-o OUTPUT] [--start-year START_YEAR] [--end-year END_YEAR] [input_file] [output_file]
```

#### Parameter Description

- `input_file`: Input grade CSV file path (must contain 'Hashed ID' column)
- `output_file`: Output CSV file path (default: converted_grades.csv)
- `-i, --input`: Input file path (optional parameter format)
- `-o, --output`: Output file path (optional parameter format)
- `--start-year`: Starting year (default: 2023)
- `--end-year`: Ending year (default: 2024)
- `-h, --help`: Display help information

## Usage Examples

### Example 1: Basic Conversion
```bash
python3 hash_to_student_id.py 2025SpringCS100student_end.csv converted_grades.csv
```

### Example 2: Specify Year Range
```bash
python3 hash_to_student_id.py -i grades.csv -o output.csv --start-year 2020 --end-year 2025
```

### Example 3: Use Default Output Filename
```bash
python3 hash_to_student_id.py student_grades.csv
```

## Input File Format

The input CSV file must contain a column named `Hashed ID`, for example:

```csv
Hashed ID,Score,Grade
1234567890,85,B
9876543210,92,A
...
```

## Output File Format

The converted CSV file will contain a `Student ID` column (replacing the original hashed ID), for example:

```csv
Student ID,Score,Grade
2024121001,85,B
2024122015,92,A
...
```

## How It Works

1. **Hash Algorithm**: Uses FNV-1a algorithm to calculate 32-bit hash values of student IDs
2. **Student ID Format**: Supports 10-digit student ID format: `YYYY + Major Code(3 digits) + Serial Number(3 digits)`
3. **Mapping Generation**: Generates complete hash-to-student-ID mapping table based on specified year range and major codes
4. **Batch Conversion**: Reads grade files and batch converts all hashed IDs

## Important Notes

- Ensure the input file contains a `Hashed ID` column
- The conversion process may take some time, especially with larger year ranges
- Hashed IDs without corresponding student IDs will retain their original values
- It's recommended to adjust `--start-year` and `--end-year` parameters based on actual student ID years for improved efficiency

## License

This project follows the corresponding open source license, see the `license` file for details.
