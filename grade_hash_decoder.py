#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import pandas as pd
import sys
import argparse
import os
from tqdm import tqdm

def hash_student_id_fnv1a(key_string):
    """
    使用FNV-1a算法对组合字符串进行哈希
    按照官方说明：学号+UID直接连接，然后FNV-1a 32位哈希
    """
    hash_value = 2166136261  # FNV offset basis
    for byte in key_string.encode('utf-8'):
        hash_value ^= byte
        hash_value = (hash_value * 16777619) % (2**32)  # FNV prime
    return hash_value

def read_student_email_mapping(file_path):
    """读取学号和邮箱的映射关系"""
    mapping = {}
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  # 跳过表头
        for row in reader:
            if len(row) >= 18:  # 确保有足够的列
                student_id = row[-1].strip()  # 最后一列是编号（学号）
                email = row[8].strip()  # 第9列是电子邮件
                if student_id and email and '@' in email:
                    mapping[student_id] = email
    return mapping

def read_uid_email_mapping(file_path):
    """读取UID和邮箱的映射关系"""
    mapping = {}
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  # 跳过表头
        for row in reader:
            if len(row) >= 4:
                uid = row[0].strip()  # 第一列是UID
                email = row[3].strip()  # 第四列是email
                if uid and email and '@' in email:
                    mapping[email] = uid
    return mapping

def build_hash_mapping(student_email_mapping, uid_email_mapping):
    """
    构建哈希到学号的映射
    按照官方说明：10位学号直接连接数字UID，然后FNV-1a哈希
    """
    print("正在构建哈希映射...")
    
    hash_to_student = {}
    
    # 通过邮箱匹配学号和UID
    for student_id, email in student_email_mapping.items():
        if email in uid_email_mapping:
            uid = uid_email_mapping[email]
            
            # 按照官方说明：学号直接连接UID（无空格）
            combined_key = f"{student_id}{uid}"
            
            # 计算FNV-1a哈希
            hash_value = hash_student_id_fnv1a(combined_key)
            
            hash_to_student[hash_value] = student_id
            
            print(f"学号: {student_id}, UID: {uid}, 组合: {combined_key}, 哈希: {hash_value}")
    
    print(f"构建了 {len(hash_to_student)} 个哈希映射")
    return hash_to_student

def convert_grade_file(grade_file, output_file, number_email_file, uid_email_file):
    """转换成绩文件中的哈希ID为学号"""
    
    # 检查输入文件是否存在
    for file_path in [grade_file, number_email_file, uid_email_file]:
        if not os.path.exists(file_path):
            print(f"错误：文件 '{file_path}' 不存在")
            return False
    
    # 读取映射关系
    print("读取学号-邮箱映射...")
    student_email_mapping = read_student_email_mapping(number_email_file)
    print(f"加载了 {len(student_email_mapping)} 个学号-邮箱映射")
    
    print("读取UID-邮箱映射...")
    uid_email_mapping = read_uid_email_mapping(uid_email_file)
    print(f"加载了 {len(uid_email_mapping)} 个UID-邮箱映射")
    
    if not student_email_mapping or not uid_email_mapping:
        print("无法加载必要的映射文件，程序退出")
        return False
    
    # 构建哈希映射
    hash_to_student = build_hash_mapping(student_email_mapping, uid_email_mapping)
    
    if not hash_to_student:
        print("错误：无法构建哈希映射")
        return False
    
    try:
        # 读取成绩文件
        print(f"正在读取成绩文件: {grade_file}")
        df = pd.read_csv(grade_file)
        
        # 检查第一列是否为哈希值
        hash_column = df.columns[0]
        print(f"哈希列名: {hash_column}")
        
        # 转换哈希ID为学号
        converted_count = 0
        not_found_count = 0
        
        def convert_hash_to_student_id(hash_id):
            nonlocal converted_count, not_found_count
            try:
                hash_value = int(hash_id)
                if hash_value in hash_to_student:
                    converted_count += 1
                    return hash_to_student[hash_value]
                else:
                    not_found_count += 1
                    return f"UNKNOWN_{hash_id}"
            except:
                not_found_count += 1
                return f"INVALID_{hash_id}"
        
        print("正在转换哈希ID为学号...")
        df['Student_ID'] = df[hash_column].apply(convert_hash_to_student_id)
        
        # 重新排列列，将Student_ID放在第一列
        columns = ['Student_ID'] + [col for col in df.columns if col != 'Student_ID']
        df_output = df[columns]
        
        # 保存结果
        df_output.to_csv(output_file, index=False, encoding='utf-8-sig')
        
        print(f"\n转换完成！")
        print(f"成功转换: {converted_count} 个哈希ID")
        print(f"未找到对应学号: {not_found_count} 个哈希ID")
        if converted_count + not_found_count > 0:
            print(f"转换成功率: {converted_count/(converted_count+not_found_count)*100:.1f}%")
        print(f"结果已保存到: {output_file}")
        
        # 显示前几行结果
        print("\n前5行结果预览:")
        print(df_output.head().to_string())
        
        return True
        
    except Exception as e:
        print(f"处理成绩文件时出错: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(
        description='将成绩文件中的哈希ID转换为学号（基于学号+UID组合）',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""使用示例:
  python3 grade_hash_decoder.py 2025SpringCS100_final_student_end.csv converted_grades.csv number_and_email.csv uid_and_email.csv
        """)
    
    parser.add_argument('grade_file', help='输入的成绩CSV文件路径（包含哈希ID）')
    parser.add_argument('output_file', help='输出CSV文件路径')
    parser.add_argument('number_email_file', help='学号-邮箱映射文件路径')
    parser.add_argument('uid_email_file', help='UID-邮箱映射文件路径')
    
    args = parser.parse_args()
    
    print(f"成绩文件: {args.grade_file}")
    print(f"输出文件: {args.output_file}")
    print(f"学号-邮箱文件: {args.number_email_file}")
    print(f"UID-邮箱文件: {args.uid_email_file}")
    print("-" * 50)
    
    success = convert_grade_file(
        args.grade_file, 
        args.output_file, 
        args.number_email_file, 
        args.uid_email_file
    )
    
    if success:
        print(f"\n✅ 转换完成！结果已保存到 {args.output_file}")
        sys.exit(0)
    else:
        print("\n❌ 转换失败")
        sys.exit(1)

if __name__ == "__main__":
    main()