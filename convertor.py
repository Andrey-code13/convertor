import sys
import json
import re

class ConfigParser():
    def __init__(self,lines):
        self.name_pattern = r"[a-zA-Z]+"
        self.array_pattern = r"\s*<<(.*?)>>"
        self.begin_dict_pattern = r"\s*table\("
        self.str_pattern = r"\s*\'(.*?)\'"
        self.number_pattern = r"\s*([\d\.]+)"
        self.calculations_pattern = rf"\s*\?\[({self.name_pattern})\]"

        self.config_dict = {}
        self.current_dict = self.config_dict
        self.lines = lines
        self.comments = False
        self.index=0

    def parse(self):
        while self.index < len(self.lines):
            line = self.lines[self.index].strip()
            if not line or line.startswith('%'):
                self.index+=1
                continue
            if line.startswith('{'):
                self.comments = True
                self.index += 1
                continue
            if line.startswith('}'):
                self.comments = False
                self.index += 1
                continue
            if self.comments:
                self.index += 1
                continue

            if ':' in line:
                key = line[:line.find(":")].strip()
                line = line[line.find(":") + 1:].strip()
                if key in self.config_dict:
                    self.index += 1
                    continue

                if re.match(self.array_pattern, line):
                    array_values = line[line.find("<<") + 2:line.rfind(">>")]
                    self.current_dict[key] =self.parser_array(array_values)
                elif re.match(self.str_pattern, line):
                    self.current_dict[key] = line.replace("'", "").strip()
                elif re.match(self.number_pattern, line):
                    value = line.strip()
                    self.current_dict[key] = float(value) if '.' in value else int(value)
                elif re.match(self.begin_dict_pattern, line):
                    self.index+=1
                    self.current_dict[key] = self.parser_dict_column()
                elif re.match(self.calculations_pattern, line):
                    referenced_key = line[line.find("[") + 1:line.rfind("]")]
                    self.current_dict[key] = self.current_dict.get(referenced_key, "Calculation error")
            if line=="table(":
                self.config_dict=self.parser_dict_column()
            self.index += 1

    def parser_dict_column(self):
        new_dict={}
        while self.lines[self.index].strip().strip(',')!=")":
            line = self.lines[self.index].strip()
            key = line[:line.find("=>")].strip()
            line = line[line.find("=>") + 2:].strip()
            if line[-1]==',':line=line[:-1]
            if re.match(self.array_pattern, line):
                array_values = line[line.find("<<") + 2:line.rfind(">>")]
                new_dict[key] = self.parser_array(array_values)
            elif re.match(self.str_pattern, line):
                new_dict[key] = line.replace("'", "").strip()
            elif re.match(self.number_pattern, line):
                value = line.strip()
                new_dict[key] = float(value) if '.' in value else int(value)
            elif re.match(self.begin_dict_pattern, line):
                self.index += 1
                new_dict[key] = self.parser_dict_column()
            elif re.match(self.calculations_pattern, line):
                referenced_key = line[line.find("[") + 1:line.rfind("]")]
                new_dict[key] = self.current_dict.get(referenced_key, "Ошибка вычислений")
            self.index += 1
        return new_dict

    def parser_dict_row(self,new_array):
        new_dict = {}
        array_dict = new_array[7:-2].split('\n')
        k = 0
        while k < len(array_dict):
            line = array_dict[k].strip()
            key = line[:line.find("=>")].strip()
            line = line[line.find("=>") + 2:].strip()
            if line[-1] == ',': line = line[:-1]
            if re.match(self.array_pattern, line):
                array_values = line[line.find("<<") + 2:line.rfind(">>")]
                new_dict[key] = self.parser_array(array_values)
            elif re.match(self.str_pattern, line):
                new_dict[key] = line.replace("'", "").strip()
            elif re.match(self.number_pattern, line):
                value = line.strip()
                new_dict[key] = float(value) if '.' in value else int(value)
            elif re.match(self.begin_dict_pattern, line):
                k += 1
                new_dict[key] = self.parser_dict_row(line)
            elif re.match(self.calculations_pattern, line):
                referenced_key = line[line.find("[") + 1:line.rfind("]")]
                new_dict[key] = self.current_dict.get(referenced_key, "Ошибка вычислений")
            k += 1
        return new_dict
    def parser_array(self, parser_line):
        new_array = []
        i = 0
        array=parser_line.strip().split(',')
        while i < len(array):
            if "<<" in array[i]:
                current_str=array[i].strip()
                i += 1
                while ">>" not in array[i]:
                    current_str=current_str+","+array[i]
                    i += 1
                current_str = current_str+","+array[i]
            elif "table(" in array[i]:
                current_str = "table(\n"+array[i].strip()[6:]
                i += 1
                while ")" not in array[i]:
                    current_str = current_str + ",\n" + array[i].strip()
                    i += 1
                current_str=current_str + ",\n" + array[i][:-1].strip()+"\n)"
            elif "?" in array[i]:
                referenced_key = array[i][array[i].find("[") + 1:array[i].rfind("]")]
                current_str = self.current_dict.get(referenced_key, "Calculation error")
            else:

                current_str=array[i].strip().replace('\'','')
            i+=1
            new_array.append(current_str)

        j=0
        while j < len(new_array):
            if "<<" in new_array[j]:
                new_array[j] = self.parser_array(new_array[j][new_array[j].find("<<") + 2:new_array[j].rfind(">>")])
            elif "table" in new_array[j]:
                new_array[j] = self.parser_dict_row(new_array[j])

            j+=1


        return new_array




    def save_to_json(self, output_file):
        with open(output_file, 'w') as json_file:
            json.dump(self.config_dict, json_file, indent=4)







def main():
    if len(sys.argv) != 2:
        print("Usage: python config_parser.py <path_to_config_file>")
        sys.exit(1)

    config_file_path = sys.argv[1]

    try:
        with open(config_file_path, 'r') as file:
            lines = file.readlines()
        parser=ConfigParser(lines)
        parser.parse()
        for k in parser.config_dict.copy().keys():
            if not(isinstance(parser.config_dict[k], dict) or isinstance(parser.config_dict[k], list)):
                parser.config_dict.pop(k)
        parser.save_to_json("output.json")
        print(json.dumps(parser.config_dict, indent=4))

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()