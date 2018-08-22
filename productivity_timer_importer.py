# Django exec(open('productivity_timer_importer.py').read())
import django
django.setup()
from pomodoro.models import Project, Pomodoro

# Pandas
import pandas as pd
from pandas.io.json import json_normalize

import json
import datetime
import pytz

file = open('./Backup_2018-08-21_15-25-34.pctb')
data = json.loads(file.read())

df_work_units = json_normalize(data['workUnits'])
df_projects = json_normalize(data['projects'])


def time_date_to_datetime(time, date):
    date = date.split("/")
    year = int(date[0])
    month = int(date[1])
    day = int(date[2])
    time = datetime.datetime.fromtimestamp(time)
    return datetime.datetime(year=year, month=month, day=day, hour=int(time.strftime("%H")), minute=int(time.strftime("%M")), second=int(time.strftime("%S")), tzinfo=pytz.UTC)


def format_work_units(df_original):
    new_column_names = {'_d': 'duration', '_dt': 'date',
                        '_id': 'id', '_p': 'project_id', '_t': 'time'}
    df = df_original.copy()
    df['_d'] = df['_d'].apply(lambda x: int(x/60))
    df.rename(columns=new_column_names, inplace=True)
    df = df.drop("_msc", 1)
    df = df.drop("_f", 1)
    df = df.drop("_m", 1)
    return df


def format_projects(df_original):
    new_column_names = {'_d': 'duration', '_id': 'id', '_l': 'last_activity',
                        '_n': 'project_name', '_s': 'state', '_p': 'parent_project',
                        '_t': 'creation_date', '_w': 'pomodoro_duration'}
    df = df_original.copy()
    #df['_d'] = df['_d'].apply(lambda x: total_time(x))
    df['_l'] = df['_l'].apply(lambda x: datetime.datetime.fromtimestamp(x))
    df['_t'] = df['_t'].apply(lambda x: datetime.datetime.fromtimestamp(x))
    df.rename(columns=new_column_names, inplace=True)
    return df

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~|Projects|~~~~~~~~~~~~~~~~~~~~~~```````


projects = {}
for index, project_sample in format_projects(df_projects).iterrows():
    project = Project.objects.create(creation_date=project_sample.creation_date,
                                     name=project_sample.project_name,
                                     user_id=2,
                                     pomodoro_duration=project_sample.pomodoro_duration)
    projects[project_sample.id] = project

for index, sample1 in format_work_units(df_work_units).iterrows():
    date = time_date_to_datetime(sample1.time, sample1.date)
    pomodoro = Pomodoro()
    pomodoro.project = projects[sample1.project_id]
    pomodoro.user_id = 2
    pomodoro.date = date
    pomodoro.duration = sample1.duration
    pomodoro.save()
