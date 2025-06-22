# Open-CS100
A Better One without nonsense.  

## **🫡Great force creates miracles. & Salute the legendary CS100 TA.**  
  
> "Because the mapping is one-way, the full table can be shared without leaking anyone’s ID."  

**Reality:** Because the student IDs are public, the mapping can be easily unmapped.
  
> "Student IDs, whether raw or hashed, are personal data."  

**Reality:** Seriously? Hashed student IDs are ‘personal data’ but publishing grades is fine? Get your priorities straight — grades > raw ID > hashed ID.  

> "Likewise, viewing or attempting to view any grade other than your own is prohibited."  

**Reality:** If viewing others' grades is prohibited, then don’t share everyone’s grades in a single XLSX file. Hashed IDs ≠ privacy. In case you don't know, there are platforms for this — they're called Blackboard and Gradescope.😄  

## Tool Description

This project contains student ID hash conversion tools for converting hashed IDs in grade files back to real student IDs.

### hash_to_student_id.py

This is the original Python script designed to convert hashed student IDs in CS100 course grade files back to real student IDs. The tool uses the FNV-1a hash algorithm to generate student ID mapping tables and supports batch conversion of student IDs across multiple years.
**Key Features:**
- 🔄 **Hash ID Conversion**: Convert hashed IDs in grade files to real student IDs
- 📅 **Multi-year Support**: Support for generating student ID mappings within specified year ranges
- 🎯 **High Coverage**: Includes extensive major codes to improve conversion success rate
- 📊 **Progress Display**: Real-time display of conversion progress and statistics
- 💾 **Result Saving**: Automatically save conversion results to new CSV files
### grade_hash_decoder.py

This is a new tool developed to handle the updated TA requirements where hashes are generated from student ID + UID combinations. It uses actual student data files to perform accurate hash-to-student-ID conversion.

**Key Features:**
- 📊 **Data-driven approach**: Uses real student-email and UID-email mapping files
- 🔢 **Enhanced algorithm**: Implements FNV-1a hash with numerical addition (student_id + uid)
- ✅ **High accuracy**: Achieves 100% conversion rate when complete data files are available
- 🛡️ **Robust validation**: Comprehensive error handling and data verification



## Installation Requirements

Ensure your system has Python 3.6+ installed and install the following dependencies:

```bash
pip install pandas tqdm
```

## Usage

### hash_to_student_id.py
```bash
python3 hash_to_student_id.py <input_file> [output_file] [--start-year YEAR] [--end-year YEAR]
```

### grade_hash_decoder.py
```bash
python3 grade_hash_decoder.py --student_file <student_email_file> --uid_file <uid_email_file> --grade_file <grade_file> --output_file <output_file>
```



## Usage Examples

### hash_to_student_id.py

#### Example 1: Basic Conversion
```bash
python3 hash_to_student_id.py 2025SpringCS100student_end.csv converted_grades.csv
```

#### Example 2: Specify Year Range
```bash
python3 hash_to_student_id.py -i grades.csv -o output.csv --start-year 2020 --end-year 2025
```

#### Example 3: Use Default Output Filename
```bash
python3 hash_to_student_id.py student_grades.csv
```

### grade_hash_decoder.py

#### Example: Basic Usage
```bash
python3 grade_hash_decoder.py --student_file number_and_email.csv --uid_file uid_and_email.csv --grade_file grades.csv --output_file final_grades.csv
```

## File Formats

### hash_to_student_id.py

**Input**: CSV file with `Hashed ID`/`Hashed` column
```csv
Hashed ID,Score,Grade
1234567890,85,B
9876543210,92,A
```

**Output**: CSV file with `Student ID` column
```csv
Student ID,Score,Grade
2024121001,85,B
2024122015,92,A
```

### grade_hash_decoder.py

**Required Files**:
- Student-email mapping: `student_id,email`
- UID-email mapping: `uid,email`
- Grade file: `Hashed ID,Score,Grade`

**Output**: CSV file with decoded student IDs

## How It Works

**hash_to_student_id.py**: Brute-force approach using FNV-1a hash algorithm to generate mappings for all possible student IDs within specified year ranges.

**grade_hash_decoder.py**: Data-driven approach that associates student IDs with UIDs via email mappings, then generates hashes using `student_id + uid` combinations.

## Important Notes

- **hash_to_student_id.py**: Input file must contain `Hashed ID` column. Adjust year range for better efficiency.
- **grade_hash_decoder.py**: Requires student-email and UID-email mapping files. Achieves 100% success rate with complete data.

## License

This project follows the WTFPL license, you can do what the fxxk you want to freely.
