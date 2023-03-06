from pynput import mouse

from textual import events
from textual.app import App
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Static, Button, Input, DataTable, Footer, Checkbox
from textual.reactive import reactive
import math
import numpy as np
import conf
import csv
import io
from dateutil import parser
import datetime
import dateutil


class PatientTable(DataTable):

    def watch_cursor_cell(self, old, value):
        pt_id = self.data[self.cursor_cell.row][0]
        self.app.selected_pt = int(pt_id)
        self.app.create_values_table()
        self.app.show_values(pt_id)
        self.app.query_one('#capturepts').disabled = False
        return super().watch_cursor_cell(old, value)


class CephaloHelper(App):
    BINDINGS = [("ctrl+d", "toggle_dark", "Toggle dark mode"),
                ("ctrl+s", "pre_post", "Toggle (Pre | Post)")]
    CSS_PATH = "styling.css"
    angles = ['sna', 'snb', 'anb', 'aobo', 'sn-mp', 'fma', 'ui-sn', 'li-mp']
    points = ['S', 'Na','Po','Or','A','B','Me','Go','U1', 'U2', 'L1', 'L2']
    points_ref = ['S', 'Na','Po','Or','A','B','Me','Go','U1', 'U2', 'L1', 'L2']
    coord = []
    prepost_value = True
    selected_pt = 0
    points_str = '\n'.join(points)

    def on_mount(self):

        self.search_patient()
        conf.init_db()

    def compose(self):
        yield Vertical(Container(Input('',placeholder='First Name', id='fname'),
                                Input('',placeholder='Last Name', id='lname'),
                                Input('',placeholder='Phone', id='phone'),
                                Horizontal(Input(placeholder='Date of Birth', id='dob'), Static('Age: ', id='age'), id='age_cont'),
                                Horizontal(Button('Add Patient', id='addpt'),
                                        Button('Capture pts', id='capturepts', disabled=True),
                                        Button('Calculate', id='calculate', disabled=True)),
                                Static('[yellow]Pre Treatment', id='pre_post'), id='inputs'),
                        PatientTable(fixed_columns=1, zebra_stripes=True, id='patients'),
                        DataTable(fixed_columns=1, zebra_stripes=True, id='values_table'), id='vertical')
        yield Container(Static(self.points_str, id='static'), id='container')
        yield Footer()

    def action_toggle_dark(self):
        self.dark = not self.dark

    def action_pre_post(self):
        
        if self.prepost_value:
            self.query_one('#pre_post').update('[yellow]Post Treatment')
            self.prepost_value = False
        else:
            self.query_one('#pre_post').update('[yellow]Pre Treatment')
            self.prepost_value = True

    def on_input_changed(self, event: Input.Changed):
        if event.sender.id in ['fname', 'lname', 'phone']:
            self.search_patient()


    def calculate_age(self, born):
        birth_day = born.day
        birth_month = born.month
        birth_year = born.year
        day = int(datetime.date.today().day)
        month = int(datetime.date.today().month)
        year = int(datetime.date.today().year)
        if birth_year > year:
            age = year - birth_year
        else:
            age = (year - birth_year) - 1
        b = abs(month - birth_month)
        c = abs(day - birth_day)

        age2 = f'{age} years, {b} months, {c} days'
        self.query_one('#age').update(age2)

        return f'{age} years, {b} months, {c} days'

    def create_values_table(self):
        table = self.query_one('#values_table')
        table.clear()
        table.columns = []
        PT_CLMN = ['  ', 'Pre Trt', 'Post Trt', '    Summary    ']
        for c in PT_CLMN:
            table.add_column(f'{c}')
        return table

    def show_values(self, pt_id):
        if pt_id:
            values_table = self.create_values_table()
            selected_pts_list2 = conf.select_all_pt_values(int(pt_id))
            if selected_pts_list2:
                sna = f'SNA,{selected_pts_list2[0].SNA_pre},{selected_pts_list2[0].SNA_post}'
                snb = f'SNB,{selected_pts_list2[0].SNB_pre},{selected_pts_list2[0].SNB_post}'
                anb = f'ANB,{selected_pts_list2[0].ANB_pre},{selected_pts_list2[0].ANB_post}'
                fma = f'FMA,{selected_pts_list2[0].FMA_pre},{selected_pts_list2[0].FMA_post}'
                snmp = f'SNMP,{selected_pts_list2[0].SNMP_pre},{selected_pts_list2[0].SNMP_post}'
                uisn = f'UISN,{selected_pts_list2[0].UISN_pre},{selected_pts_list2[0].UISN_post}'
                limp = f'LIMP,{selected_pts_list2[0].LIMP_pre},{selected_pts_list2[0].LIMP_post}'

                selected_pts_list_str2 = "\n".join([sna, snb, anb, fma, snmp, uisn, limp])
                rows = csv.reader(io.StringIO(selected_pts_list_str2))
                values_table.add_rows(rows)

    def wt_coord(self):
        self.query_one('#calculate').disabled = False

    def search_patient(self):
        table = self.create_find_pt()
        fname = self.query_one('#fname').value
        lname = self.query_one('#lname').value
        phone = self.query_one('#phone').value
        
        if phone.isdigit():
            phone = int(phone)
        else:
            self.query_one('#phone').value = ''

        selected_pts_list = conf.select_all_starts_with_all_fields(fname, lname, phone)
        if selected_pts_list:
            selected_pts_list_str = "\n".join([str(r) for r in selected_pts_list])
            rows = csv.reader(io.StringIO(selected_pts_list_str))
            table.add_rows(rows)

        if len(selected_pts_list) == 1:
            self.query_one('#capturepts').disabled = False
            self.show_values(table.data[0][0])
        else:
            self.query_one('#capturepts').disabled = True

    def create_find_pt(self):
        table = self.query_one('#patients')
        table.clear()
        table.columns = []
        PT_CLMN = ['ID', 'First Name', 'Last Name', 'Date of Birth', 'Phone']
        for c in PT_CLMN:
            table.add_column(f'{c}')
        return table

    def on_button_pressed(self, event: Button.Pressed):
        if event.sender.id == 'addpt':
            # fname = self.query_one('#fname', Input).value
            # lname = self.query_one('#lname', Input).value
            # phone = self.query_one('#phone', Input).value
            # date_of_birth = self.query_one('#dob', Input).value

            
            fname = str(self.query_one('#fname', Input).value).capitalize()
            lname = str(self.query_one('#lname', Input).value).capitalize()
            phone = int(self.query_one('#phone', Input).value)
            date_of_birth = parser.parse(str(self.query_one('#dob', Input).value))

            age = self.calculate_age(date_of_birth)

            selected_pts_list = conf.select_all_starts_with_all_fields(fname, lname, phone)

            if not selected_pts_list:
                patient = conf.Patient(first_name=fname, last_name=lname, phone=phone, date_of_birth=date_of_birth)
                conf.save_to_db(patient)
            self.search_patient()

        elif event.sender.id == 'capturepts':
            self.query_one('#calculate').disabled = True
            # self.dark = False
            self.coord = []
            self.points = ['S', 'Na','Po','Or','A','B','Me','Go','U1', 'U2', 'L1', 'L2']
            list_str = '\n'.join(self.points)
            self.query_one('#static').update(list_str)
            mouse.Listener(on_click=self.capture_points).start()

        elif event.sender.id == 'calculate':
            self.query_one('#calculate').disabled = True
            self.calculate_angles()


    def capture_points(self, x, y, button, pressed):
        if pressed:
            index = len(self.coord)
            if 'left' in str(button):
                if index < 15:
                    self.coord.append([x, y])
                    self.points[index] = f'{self.points[index]}: {[x, y]}'
                    list_str = '\n'.join(self.points)
                    self.query_one('#static').update(list_str)
                    if len(self.coord) == 12:
                        self.wt_coord()
                        return False
            if 'right' in str(button):
                if index != 0:
                    self.coord.pop()
                    self.points[index-1] = f'{self.points_ref[index-1]}'
                    list_str = '\n'.join(self.points)
                    self.query_one('#static').update(list_str)


    def angle3pt(self, a, b, c):
        ang = math.degrees(math.atan2(c[1]-b[1], c[0]-b[0]) - math.atan2(a[1]-b[1], a[0]-b[0]))
        return round(360 - ang) if ang > 0 else round(-ang)


    def angle4pt(self, p0, p1, p2, p3):
        v0 = np.array(p0) - np.array(p1)
        v1 = np.array(p2) - np.array(p3)
        angle = np.math.atan2(np.linalg.det([v0,v1]),np.dot(v0,v1))
        return round(abs(np.degrees(angle)), 1)


    def calculate_angles(self):
        sna = self.angle3pt(self.coord[0], self.coord[1], self.coord[4])
        snb = self.angle3pt(self.coord[0], self.coord[1], self.coord[5])
        anb = sna - snb
        snmp = self.angle4pt(self.coord[0], self.coord[1], self.coord[7], self.coord[6])
        fma = self.angle4pt(self.coord[2], self.coord[3], self.coord[7], self.coord[6])
        uisn = self.angle4pt(self.coord[8], self.coord[9], self.coord[3], self.coord[2])
        limp = self.angle4pt(self.coord[10], self.coord[11], self.coord[6], self.coord[7])

        # fname = str(self.query_one('#fname', Input).value)
        # lname = str(self.query_one('#lname', Input).value)
        # phone = int(self.query_one('#phone', Input).value)
        # date_of_birth = parser.parse(str(self.query_one('#dob', Input).value))
        
        if self.selected_pt == 0:
            pt_id = int(self.query_one('#patients').data[0][0])
        else:
            pt_id = self.selected_pt


        if self.prepost_value:
            conf.update_values_pre(id=pt_id, 
                        sna=sna, snb=snb, anb=anb, snmp=snmp, 
                        fma=fma, uisn=uisn, limp=limp)
            self.show_values(pt_id)
        else:
            conf.update_values_post(id=pt_id, 
                        sna=sna, snb=snb, anb=anb, snmp=snmp, 
                        fma=fma, uisn=uisn, limp=limp)
            self.show_values(pt_id) 




if __name__ == "__main__":
    app = CephaloHelper()
    target=app.run()
