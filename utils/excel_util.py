from openpyxl import Workbook

from typing import Dict,List
import string
from stringcase import pascalcase


def set_cell_value(sheet,cell:str,value):
    sheet[cell] = value



def create_excel_from_list(info:List[Dict],file_path="workbook.xlsx"):
    wb = Workbook()

    letters=string.ascii_uppercase

    sheet = wb.active

    key_to_column = {k:letters[i] for i,k in enumerate(info[0].keys())}

    for k in key_to_column:
        set_cell_value(sheet,f"{key_to_column[k]}1",pascalcase(k))

    for i,row in enumerate(info):
        for k in row:
            set_cell_value(sheet,f"{key_to_column[k]}{i+2}",row[k])

    wb.save(file_path)