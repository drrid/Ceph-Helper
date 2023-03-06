import sqlalchemy as db
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import datetime as dt
from datetime import timedelta
import numpy as np

from dateutil import parser
import csv
import io

engine = db.create_engine('sqlite:///cephalovalues.db')
Base = declarative_base()
db_session = db.orm.sessionmaker(bind=engine, autocommit=True)
session = db_session()


# Patient Class -----------------------------------------------------------------------------------------------------------
class Patient(Base):

    __tablename__ = 'patient'
    patient_id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    phone = db.Column(db.Integer())
    date_of_birth = db.Column(db.Date())

    pretrt = db.Column(db.Boolean())
    posttrt = db.Column(db.Boolean())


    SNA_pre = db.Column(db.Float())
    SNB_pre = db.Column(db.Float())
    ANB_pre = db.Column(db.Float())
    FMA_pre = db.Column(db.Float())
    SNMP_pre = db.Column(db.Float())
    UISN_pre = db.Column(db.Float())
    LIMP_pre = db.Column(db.Float())

    SNA_post = db.Column(db.Float())
    SNB_post = db.Column(db.Float())
    ANB_post = db.Column(db.Float())
    FMA_post = db.Column(db.Float())
    SNMP_post = db.Column(db.Float())
    UISN_post = db.Column(db.Float())
    LIMP_post = db.Column(db.Float())

    def __repr__(self):
        return f'{self.patient_id},{self.first_name},{self.last_name},{self.date_of_birth},{self.phone},{self.SNA_pre},{self.SNB_pre},{self.ANB_pre},{self.FMA_pre},{self.SNMP_pre},{self.UISN_pre},{self.LIMP_pre},{self.SNA_post},{self.SNB_post},{self.ANB_post},{self.FMA_post},{self.SNMP_post},{self.UISN_post},{self.LIMP_post}'
#---------------------------------------------------------------------------------------------------------------------------


def init_db():
    Base.metadata.create_all(engine)
    Base.metadata.bind = engine

def save_to_db(record):
    try:
        session.add(record)
        session.commit()
    except Exception as e:
        print(e) 

def update_values_pre(id, sna, snb, anb, fma, snmp, uisn, limp):
    try:
        session.query(Patient).filter(Patient.patient_id == id).update({Patient.SNA_pre: sna, Patient.SNB_pre: snb, Patient.ANB_pre: anb,
                                                                        Patient.FMA_pre: fma, Patient.SNMP_pre: snmp, Patient.UISN_pre: uisn,
                                                                        Patient.LIMP_pre: limp, Patient.pretrt: True})
        session.commit()
    except Exception as e:
        print(e)

def update_values_post(id, sna, snb, anb, fma, snmp, uisn, limp):
    try:
        session.query(Patient).filter(Patient.patient_id == id).update({Patient.SNA_post: sna, Patient.SNB_post: snb, Patient.ANB_post: anb,
                                                                        Patient.FMA_post: fma, Patient.SNMP_post: snmp, Patient.UISN_post: uisn,
                                                                        Patient.LIMP_post: limp, Patient.posttrt: True})
        session.commit()
    except Exception as e:
        print(e)

# def select_one_first_name(first_name):
#     try:
#         return session.query(patient).filter_by(patient.first_name == first_name).one()
#     except Exception as e:
#         print(e)

# def select_one_id(id):
#     try:
#         return session.query(patient).filter(patient.patient_id == id).one()
#     except Exception as e:
#         print(e)

# def select_all(first_name):
#     try:
#         return session.query(patient).filter_by(patient.first_name == first_name).all()
#     except Exception as e:
#         print(e)

# def select_all_contains(first_name):
#     try:
#         return session.query(patient).filter(patient.first_name.contains(first_name))
#     except Exception as e:
#         print(e)

# def select_all_starts_with(q):
#     try:
#         return [r for r in session.query(patient).filter(patient.first_name.startswith(q))]
#     except Exception as e:
#         print(e)

def select_all_starts_with_all_fields(fname, lname, phone):
    try:
        return [r for r in session.query(Patient).filter(Patient.first_name.startswith(fname),
                                                        Patient.last_name.startswith(lname),
                                                        Patient.phone.startswith(phone))]
    except Exception as e:
        print(e)

# def select_all_starts_with_phone(q):
#     try:
#         return [r for r in session.query(patient).filter(patient.phone.startswith(q))]
#     except Exception as e:
#         print(e)

# def select_all_starts_with_lname(q):
#     try:
#         return [r for r in session.query(patient).filter(patient.last_name.startswith(q))]
#     except Exception as e:
#         print(e)

# def select_all_encounters():
#     try:
#         return session.query(Encounter).all()
#     except Exception as e:
#         print(e)

# def select_encounter(q):
#     try:
#         return session.query(Encounter).filter(Encounter.rdv == q.rdv).one()
#     except Exception as e:
#         print(e)

def select_all_pt_values(id):
    try:
        return [r for r in session.query(Patient).filter(Patient.patient_id == id).all()]
    except Exception as e:
        print(e)

# def select_week_encounters(start, end):
#     try:
#         return session.query(Encounter).filter(Encounter.rdv.between(start, end)).all()
#     except Exception as e:
#         print(e)

# def select_patient_encounters(id):
#     try:
#         return session.query(Encounter).filter(Encounter.patient_id == id).all()
#     except Exception as e:
#         print(e)


# def get_weekly_start_end(ind):
#     # print(ind)
#     if ind < 0:
#         today_date = dt.datetime.today() - timedelta(days=ind*-6)
#     else:
#         today_date = dt.datetime.today() + timedelta(days=ind*6)

#     SHIFTED_INDEX = {0:2, 1:3, 2:4, 3:5, 4:6, 5:0, 6:1}

#     today_index = today_date.weekday()
#     shifted_index = SHIFTED_INDEX[today_index]
#     current_week = today_date - timedelta(days=shifted_index)

#     hour_start = 0
#     minute_start = 0
#     day_start = current_week.day
#     year_start = current_week.year
#     month_start = current_week.month

#     current_week_start = dt.datetime(year_start, month_start, day_start, hour_start, minute_start)
#     current_week_end = current_week_start + timedelta(days=6)

#     day_end = current_week_end.day
#     year_end = current_week_end.year
#     month_end = current_week_end.month
#     hour_end = 23
#     minute_end = 59


#     current_week_end_final = dt.datetime(year_end, month_end, day_end, hour_end, minute_end)
    
#     return (current_week_start, current_week_end_final)


# def get_weekly_encounters_csv(result):
#     rows = ['9:00', '9:30', '10:00', '10:30', 
#         '11:00', '11:30', '12:00', '12:30', 
#         '13:00', '13:30', '14:00', '14:30', 
#         '15:00', '15:30']

#     dict_row = {'9:0':0,'9:30':1,'10:0':2,'10:30':3,
#         '11:0':4,'11:30':5,'12:0':6,'12:30':7,
#         '13:0':8,'13:30':9,'14:0':10,'14:30':11,
#         '15:0':12,'15:30':13}

#     dict_column = {0:2, 1:3, 2:4, 3:5, 4:6, 5:0, 6:1}  

#     coor_array = []
#     patients = []
#     # weekly_matrix = np.zeros((14,7), dtype=object)

#     weekly_matrix = np.full((14,7), dtype=object, fill_value='_')

#     for r in result:
#         rdv_time = f'{r.rdv.hour}:{r.rdv.minute}'
#         row = dict_row[rdv_time]
#         clm = dict_column[r.rdv.weekday()]
#         coor_array.append([row, clm])
#         patient = select_one_id(r.patient_id)
#         patients.append(patient.first_name + ' ' + patient.last_name + ' ' + str(patient.patient_id))

#     for i, (x, y) in enumerate(coor_array):
#         weekly_matrix[x,y] = patients[i]
    
#     arr2 = weekly_matrix.flatten()

#     for i, v in enumerate(arr2):
#         index = int(i/7)
#         rows[index] = rows[index] + ',' + str(v)

#     pretty = '\n'.join(rows)
#     return pretty






# patient = Patient(first_name='dfdfdf', last_name='sss', phone=3234324, 
#                     SNA_pre=45, SNB_pre=55, ANB_pre=4, SNMP_pre=2, 
#                     FMA_pre=1, UISN_pre=7, LIMP_pre=5, pretrt=True)

# save_to_db(patient)


