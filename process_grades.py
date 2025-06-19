#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import pandas as pd
import sys
import argparse
import os

def hash_student_id_fnv1a(student_id):
    FNV_OFFSET_BASIS = 2166136261
    FNV_PRIME = 16777619
    
    id_str = str(student_id).zfill(10)
    
    hash_value = FNV_OFFSET_BASIS
    
    for i in range(10):
        if i < len(id_str):
            byte = ord(id_str[i])
        else:
            byte = ord('0')
        
        hash_value ^= byte
        hash_value = (hash_value * FNV_PRIME) % (2**32)
    
    return hash_value

def process_student_grades(student_file, grades_file, output_file):

    if not os.path.exists(student_file):
        print(f"错误：学生信息文件 '{student_file}' 不存在")
        return False
    
    if not os.path.exists(grades_file):
        print(f"错误：成绩文件 '{grades_file}' 不存在")
        return False
    
    students = []
    try:
        with open(student_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader)
            for row in reader:
                if len(row) >= 3:
                    name = row[0]
                    student_id = row[1]
                    phone = row[2]
                    students.append({
                        'name': name,
                        'student_id': student_id,
                        'phone': phone
                    })
    except UnicodeDecodeError:
        encodings = ['gbk', 'gb2312', 'utf-8-sig']
        for encoding in encodings:
            try:
                with open(student_file, 'r', encoding=encoding) as f:
                    reader = csv.reader(f)
                    header = next(reader)
                    for row in reader:
                        if len(row) >= 3:
                            name = row[0]
                            student_id = row[1]
                            phone = row[2]
                            students.append({
                                'name': name,
                                'student_id': student_id,
                                'phone': phone
                            })
                break
            except UnicodeDecodeError:
                continue
    except Exception as e:
        print(f"读取学生信息文件时出错: {e}")
        return False
    
    print(f"读取到 {len(students)} 个学生信息")
    
    try:
        grades_df = pd.read_csv(grades_file)
        print(f"读取到 {len(grades_df)} 条成绩记录")
    except Exception as e:
        print(f"读取成绩文件时出错: {e}")
        return False
    
    grade_columns = grades_df.columns.tolist()
    
    results = []
    matched_count = 0
    
    for student in students:
        student_id = student['student_id']
        
        hash_value = hash_student_id_fnv1a(student_id)
        
        grade_row = grades_df[grades_df['Hashed ID'] == hash_value]
        
        if not grade_row.empty:
            matched_count += 1
            grade_data = grade_row.iloc[0].to_dict()
            
            result_row = {
                '姓名': student['name'],
                '学号': student['student_id'],
                '电话': student['phone']
            }
            
            for col in grade_columns:
                if col != 'Hashed ID':
                    result_row[col] = grade_data[col]
            
            results.append(result_row)
            print(f"匹配成功: {student['name']} ({student_id}) -> 哈希值: {hash_value}")
        else:
            print(f"未找到匹配: {student['name']} ({student_id}) -> 哈希值: {hash_value}")
    
    print(f"\n总共匹配成功 {matched_count}/{len(students)} 个学生")
    
    if results:
        try:
            results_df = pd.DataFrame(results)
            results_df.to_csv(output_file, index=False, encoding='utf-8-sig')
            print(f"\n结果已保存到 {output_file}，包含 {len(results)} 条记录")
            
            print("\n前5行结果预览:")
            print(results_df.head().to_string())
            return True
        except Exception as e:
            print(f"保存结果文件时出错: {e}")
            return False
    else:
        print("\n没有匹配的结果")
        return False

def main():
    parser = argparse.ArgumentParser(
        description='处理学生成绩数据，将哈希ID转换为真实学号并匹配姓名电话',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""使用示例:
  python3 process_grades.py 姓名学号电话.csv 2025SpringCS100student_end.csv results.csv
  python3 process_grades.py -s students.csv -g grades.csv -o output.csv
        """)
    
    parser.add_argument('student_file', nargs='?', 
                       help='学生信息CSV文件路径（包含姓名、学号、电话）')
    parser.add_argument('grades_file', nargs='?',
                       help='成绩CSV文件路径（包含哈希ID和成绩）')
    parser.add_argument('output_file', nargs='?', default='results.csv',
                       help='输出CSV文件路径（默认: results.csv）')
    
    parser.add_argument('-s', '--student', dest='student_file_alt',
                       help='学生信息CSV文件路径')
    parser.add_argument('-g', '--grades', dest='grades_file_alt',
                       help='成绩CSV文件路径')
    parser.add_argument('-o', '--output', dest='output_file_alt',
                       help='输出CSV文件路径')
    
    args = parser.parse_args()
    
    student_file = args.student_file_alt or args.student_file
    grades_file = args.grades_file_alt or args.grades_file
    output_file = args.output_file_alt or args.output_file or 'results.csv'
    
    if not student_file or not grades_file:
        parser.print_help()
        print("\n错误：必须提供学生信息文件和成绩文件路径")
        sys.exit(1)
    
    print(f"学生信息文件: {student_file}")
    print(f"成绩文件: {grades_file}")
    print(f"输出文件: {output_file}")
    print("-" * 50)
    
    success = process_student_grades(student_file, grades_file, output_file)
    
    if success:
        print(f"\n✅ 处理完成！结果已保存到 {output_file}")
        sys.exit(0)
    else:
        print("\n❌ 处理失败")
        sys.exit(1)

if __name__ == "__main__":
    main()