import pandas as pd
import numpy as np
import os
import glob
import matplotlib.pyplot as plt


def preprocess_emergencias(path):
  """
  Function that preprocesses 'emergencias' csv from Pentaho.
  
  Args:
    path (str): Path to csv to preprocess

  Returns:
    Preprocessed pandas dataframe
  """
  # Read csv
  df_temp = pd.read_csv(path)

  # Get rid of unnecessary columns
  df_temp.drop(columns=[f'Unnamed: {i}' for i in range(18,27,1)], inplace=True)
  df_temp.drop(columns=['Unnamed: 0','Unnamed: 7','Unnamed: 10'], inplace=True)

  # Get rid of unnecessary rows
  df_temp.drop(range(0,6), inplace=True)

  # Set definitive columns
  columns = ['DNI', 'NHC', 'PACIENTE', 'SEXO', 'EDAD', 'FECHA_HORA_INGRESO', 
          'SERVICIO', 'SECCION', 'ALTA_MEDICA', 'MOTIVO_ALTA', 'ALTA_ADMIN', 
          'PROFESIONAL', 'DIAGNOSTICO', 'CIE10', 'DESC_CIE10']
  df_temp.columns=columns

  # Convert dates to datetype format
  df_temp['ALTA_ADMIN'] = pd.to_datetime(df_temp['ALTA_ADMIN'], dayfirst=True)
  df_temp['ALTA_MEDICA'] = pd.to_datetime(df_temp['ALTA_MEDICA'], dayfirst=True)
  df_temp['FECHA_HORA_INGRESO'] = pd.to_datetime(df_temp['FECHA_HORA_INGRESO'], dayfirst=True)

  # Create time difference columns
  df_temp['DIF_ALTA_ADMIN_MEDICA'] = df_temp['ALTA_ADMIN'] - df_temp['ALTA_MEDICA']
  df_temp['DIF_ALTA_MEDICA_INGRESO'] = df_temp['ALTA_MEDICA'] - df_temp['FECHA_HORA_INGRESO']
  df_temp['ESTADIA_TOTAL'] = df_temp['ALTA_ADMIN'] - df_temp['FECHA_HORA_INGRESO']

  # Sort by 'FECHA_HORA_INGRESO'
  df_temp.sort_values('FECHA_HORA_INGRESO', inplace=True)

  # Convert numerical srt values to int
#  df['EDAD'] = df['EDAD'].astype(int)
#  df['DNI'] = df['DNI'].astype(int)
#  df['NHC'] = df['NHC'].astype(int)

  # Reset index
  df_temp.reset_index(drop=True, inplace=True)
  return df_temp


def concatenate_dfs(df_list):
  """
  Function that merges all preprocessed dfs in a directory, filtered by keyword

  Args:
    df_list (list): list of dataframes to be concatenated.
  
  Returns:
    Concatenation of all pandas dataframes in lis.
  """
  df = pd.concat(df_list)
  df['EDAD'] = df['EDAD'].astype(int)
#  df['DNI'] = df['DNI'].astype(int)
#  df['NHC'] = df['NHC'].astype(int)
  df.reset_index(drop=True, inplace=True)
  return df

def atenciones_por_seccion(dataframe):
  """
  Function that generates statistics from emergency dataframe

  Args:
    dataframe: pandas dataframe

  Returns:

  """
  ### Atenciones por sección

  # Dataframe
  seccion_vc = dataframe['SECCION'].value_counts(dropna=False)
  seccion = pd.DataFrame(dataframe['SECCION'].value_counts(dropna=False))
  seccion['%'] = dataframe['SECCION'].value_counts(normalize=True)*100
  seccion = seccion.reset_index()
  seccion.columns=['SECCION','CANTIDADES','% DEL TOTAL']
  print(f"          Atenciones por sección (Total = {seccion['CANTIDADES'].sum()})\n")
  display(seccion)
  print('\n\n')

  # Plot pie
  explode_values = np.arange(0,len(seccion)/10,0.1)
  explode = explode_values
  plt.figure()
  ax = seccion_vc.plot(kind='pie', figsize=(15,10), fontsize=13, autopct="%1.1f%%", explode=explode)
  ax.set_title(f"Atenciones por sección (Total = {seccion['CANTIDADES'].sum()})",fontsize=20)
  ax.set_ylabel("")
  
  # Plot bar
  plt.figure(figsize=(20,15))
  seccion_vc.plot(kind='bar',rot=45)
  plt.title(f"Atenciones por sección (Total = {seccion['CANTIDADES'].sum()})", fontsize=20)
  
def top_20_professionals(dataframe, por_seccion=False):
  # Prepare df
  df = pd.DataFrame(dataframe['PROFESIONAL'].value_counts(dropna=False)[:20])
  df['% TOTAL'] = dataframe['PROFESIONAL'].value_counts(dropna=False, normalize=True) *100
  df = df.reset_index()
  df.columns=['PROFESIONAL','ATENCIONES','% TOTAL']
  print(f'Top 20 profesionales con mayoeres atenciones en todos los servicios')
  display (df)
  print('\n')
  
  # Plot bar
  ax = df.plot.bar('PROFESIONAL', 'ATENCIONES', rot=45, figsize=(20,15))
  plt.title(f'Top 20 profesionales con mayores atenciones en todos los servicios')
  ax.set_ylabel("Cantidad de atenciones")
  ax.set_xlabel("Profesionales")

  # Write totals
  for i in ax.patches:
    ax.text(i.get_x(), i.get_height()*1.02, str(i.get_height()), fontsize=13, color='dimgrey')

  if por_seccion:
    secciones = dataframe['SECCION'].unique()
    # Dataframe loop
    for i, secc in enumerate(secciones):
      secc_temp = pd.DataFrame(dataframe[dataframe['SECCION']==secciones[i]])
      professional = pd.DataFrame(secc_temp['PROFESIONAL'].value_counts(dropna=False))[:20]
      professional['% TOTAL'] = secc_temp['PROFESIONAL'].value_counts(dropna=False, normalize=True)*100
      professional = professional.reset_index()
      professional.columns=['PROFESIONAL','ATENCIONES', '% TOTAL']
      print(f'Top 20 profesionales en atenciones de {secc}')
      display(professional)
      print('\n')
      
      # Plot bar
      ax = professional.plot.bar('PROFESIONAL', 'ATENCIONES', figsize=(20,10), fontsize=12)
      ax.set_title(f"Top 20 profesionales en atenciones de {secc}")
      ax.set_ylabel("Cantidad de atenciones")
      ax.set_xlabel("Profesionales")
      plt.xticks(rotation=45)

      # Write totals
      for i in ax.patches:
        ax.text(i.get_x(), i.get_height()*1.02, str(i.get_height()), fontsize=13, color='dimgrey')
  
def atenciones_por_hora(dataframe, por_servicio=False):
  df_horas = dataframe.FECHA_HORA_INGRESO.dt.hour.value_counts()
  df_horas = df_horas.sort_index()

  # Plot total
  plt.figure()
  ax = df_horas.plot(kind='bar', fontsize=13, figsize=(15,10), color="orange")
  ax.set_title("Cantidad de atenciones según la hora | TOTAL | GUARDIA | 2021")
  ax.set_ylabel("Atenciones")
  plt.xticks(rotation=0)

  for i in ax.patches:
    if i.get_height() < 1000:
      ax.text(i.get_x()-i.get_width()/4, i.get_height()*1.02, str(int(i.get_height())), fontsize=13, color='dimgrey')
    else:
      ax.text(i.get_x()-i.get_width()/2, i.get_height()*1.01, str(int(i.get_height())), fontsize=13, color='dimgrey')

  if por_servicio:
    secciones = dataframe['SECCION'].unique()

    # Loop plot by seccion
    for i, secc in enumerate(secciones):
      secc_temp = pd.DataFrame(dataframe[dataframe['SECCION']==secciones[i]])
      df_horas_temp = secc_temp.FECHA_HORA_INGRESO.dt.hour.value_counts()
      df_horas_temp = df_horas_temp.sort_index()

      # Plot
      plt.figure()
      ax = df_horas_temp.plot(kind='bar', fontsize=13, figsize=(15,10), color="orange")
      ax.set_title(f"Cantidad de atenciones según la hora | {secc} | GUARDIA | 2021")
      ax.set_ylabel("Atenciones")
      plt.xticks(rotation=0)

      for i in ax.patches:
        if i.get_height() < 1000:
          ax.text(i.get_x()-i.get_width()/4, i.get_height()*1.02, str(int(i.get_height())), fontsize=13, color='dimgrey')
        else:
          ax.text(i.get_x()-i.get_width()/2, i.get_height()*1.01, str(int(i.get_height())), fontsize=13, color='dimgrey')

def atenciones_por_dia_semana(dataframe, por_seccion):
  # Df prepare
  df_dias = dataframe['FECHA_HORA_INGRESO'].dt.dayofweek.value_counts()
  df_dias.sort_index(inplace=True)
  df_dias = df_dias.rename({0:'Lunes', 1:'Martes', 2:'Miércoles', 3:'Jueves', 4:'Viernes', 5:'Sábado', 6:'Domingo'})

  # Plot
  plt.figure()
  ax = df_dias.plot(kind='bar', fontsize=13, figsize=(15,10), colormap="jet")
  ax.set_title("Cantidad de atenciones en todos los servicios por día de la semana")
  ax.set_ylabel("Atenciones")
  plt.xticks(rotation=0)

  # Write totals
  for i in ax.patches:
    ax.text(i.get_x() + 0.1, i.get_height()*1.02, str(int(i.get_height())), fontsize=13, color='dimgrey')

  if por_seccion:
    # Df by seccion
    secciones = dataframe['SECCION'].unique()

    for i, secc in enumerate(secciones):
      secc_temp = pd.DataFrame(dataframe[dataframe['SECCION']==secciones[i]])
      df_dias = secc_temp['FECHA_HORA_INGRESO'].dt.dayofweek.value_counts()
      df_dias.sort_index(inplace=True)
      df_dias = df_dias.rename({0:'Lunes', 1:'Martes', 2:'Miércoles', 3:'Jueves', 4:'Viernes', 5:'Sábado', 6:'Domingo'})

      # Plot
      plt.figure(figsize=(15,15))
      ax = df_dias.plot(kind='bar', fontsize=13, figsize=(15,10), colormap="jet")
      ax.set_title(f"Cantidad de atenciones en {secc} por día de la semana")
      ax.set_ylabel("Atenciones")
      plt.xticks(rotation=0)

      # Write totals
      for i in ax.patches:
        ax.text(i.get_x() + 0.1, i.get_height()*1.02, str(int(i.get_height())), fontsize=13, color='dimgrey')

def atenciones_grupo_etareo(dataframe):
  # Group classifier
  grupos = [0,0,0,0,0,0]
  for i in range(len(dataframe.EDAD)):
    if dataframe.EDAD[i] == 0:
      grupos[0] = grupos[0] + 1
    elif dataframe.EDAD[i] > 0 and dataframe.EDAD[i] < 14:
      grupos[1] = grupos[1] + 1
    elif dataframe.EDAD[i] > 14 and dataframe.EDAD[i] < 22:
      grupos[2] = grupos[2] + 1
    elif dataframe.EDAD[i] > 22 and dataframe.EDAD[i] < 41:
      grupos[3] = grupos[3] + 1
    elif dataframe.EDAD[i] > 41 and dataframe.EDAD[i] < 61:
      grupos[4] = grupos[4] + 1
    else:
      grupos[5] = grupos[5] + 1

  # Plot  
  plt.figure()  
  labels=['0 años', '1 a 13', '14 a 21', '22 a 40', '41 a 60', '+61']
  fig = plt.figure(figsize=(15,10))
  explode=[0.1,0.1,0.1,0,0.1,0.1]
  plt.pie(grupos, labels=labels, autopct='%1.2f%%', explode=explode)
  plt.title("Atenciones según grupo etáreo | EMERGENCIAS");

  # By seccion
  secciones = dataframe['SECCION'].unique()

  for j, secc in enumerate(secciones):
    secc_temp = pd.DataFrame(dataframe[dataframe['SECCION']==secciones[j]])
    secc_temp.reset_index(drop=True, inplace=True)
    grupos = [0,0,0,0,0,0]
    for k in range(len(secc_temp.EDAD)):
      if secc_temp.EDAD[k] == 0:
        grupos[0] = grupos[0] + 1
      elif secc_temp.EDAD[k] > 0 and secc_temp.EDAD[k] < 14:
        grupos[1] = grupos[1] + 1
      elif secc_temp.EDAD[k] > 14 and secc_temp.EDAD[k] < 22:
        grupos[2] = grupos[2] + 1
      elif secc_temp.EDAD[k] > 22 and secc_temp.EDAD[k] < 41:
        grupos[3] = grupos[3] + 1
      elif secc_temp.EDAD[k] > 41 and secc_temp.EDAD[k] < 61:
        grupos[4] = grupos[4] + 1
      else:
        grupos[5] = grupos[5] + 1
      
    # Plot 
    plt.figure()   
    labels=['0 años', '1 a 13', '14 a 21', '22 a 40', '41 a 60', '+61']
    fig = plt.figure(figsize=(15,10))
    explode=[0.1,0.1,0.1,0,0.1,0.1]
    plt.pie(grupos, labels=labels, autopct='%1.2f%%', explode=explode)
    plt.title(f"Atenciones en {secc} según grupo etáreo | EMERGENCIAS");
    
def motivo_alta(dataframe):
  df_display = pd.DataFrame(dataframe['MOTIVO_ALTA'].value_counts(dropna=False))
  df_display = df_display.reset_index()
  df_display.columns=['MOTIVO_ALTA', 'CANTIDAD']
  display(df_display)
  print('\n')
  ax = dataframe['MOTIVO_ALTA'].value_counts(dropna=False).plot(kind='barh', figsize=(15,10))
  ax.set_title("Motivo de alta")

  for i in ax.patches:
    if i.get_width() > 1000:
      ax.text(i.get_width() - 600, i.get_y() + 0.20, str(i.get_width()), fontsize=13, color='white')
    else:
      ax.text(i.get_width() + 20, i.get_y() + .20, str(i.get_width()), fontsize=13, color='black')


def top_20_cod_diagnostics(dataframe, por_seccion):
  # Df prep
  sin_cod = dataframe['CIE10'].isna().sum()
  total_atenciones = len(dataframe.CIE10)

  # Plot
  plt.figure()
  ax = dataframe['CIE10'].value_counts()[:20].plot(kind="bar", figsize=(15,10), fontsize=13, color="brown")
  ax.set_title(f"Top 20 diagnósticos codificados con CIE10\nDiagnósticos sin codificar: {sin_cod} | Diagnósticos totales: {total_atenciones}", fontsize=20)
  plt.xticks(rotation=20)

  # Write totals
  for i in ax.patches:
    if i.get_height() < 100:
      ax.text(i.get_x()*1.01, i.get_height() + 2, str(i.get_height()), fontsize=13, color='grey')
    else:
      ax.text(i.get_x()*1.02, i.get_height() + 2, str(i.get_height()), fontsize=13, color='grey')
  
  if por_seccion:
    # By seccion
    secciones = dataframe['SECCION'].unique()
    for i, secc in enumerate(secciones):
      secc_temp = pd.DataFrame(dataframe[dataframe['SECCION']==secciones[i]])
      sin_cod_temp = secc_temp['CIE10'].isna().sum()
      total_atenciones_temp = len(secc_temp.CIE10)

      if len(secc_temp['CIE10'].value_counts(dropna=False)) > 1:
        plt.figure()
        ax = secc_temp['CIE10'].value_counts()[:20].plot(kind="bar", figsize=(15,10), fontsize=13, color="brown")
        ax.set_title(f"Top 20 diagnósticos codificados con CIE10 en {secc}\nDiagnósticos sin codificar: {sin_cod_temp} | Diagnósticos totales: {total_atenciones_temp}", fontsize=20)
        plt.xticks(rotation=20)
      else:
        plt.figure()
        ax = secc_temp['CIE10'].value_counts(dropna=False).plot(kind="bar", figsize=(15,10), fontsize=13, color="brown")
        ax.set_title(f"Top 20 diagnósticos codificados con CIE10 en {secc}\nDiagnósticos sin codificar: {sin_cod_temp} | Diagnósticos totales: {total_atenciones_temp}", fontsize=20)
        plt.xticks(rotation=20);

      # Write totals
      for i in ax.patches:
        if i.get_height() < 100:
          ax.text(i.get_x()*1.01, i.get_height()*1.02, str(i.get_height()), fontsize=13, color='grey')
        else:
          ax.text(i.get_x()*1.02, i.get_height()*1.02, str(i.get_height()), fontsize=13, color='grey') 

def promedios_tiempo(dataframe):
  print('Medias de tiempo según estado del paciente:')
  print(f"="*85)
  print(f"Entre Ingreso y Alta Médica: {dataframe['DIF_ALTA_MEDICA_INGRESO'].mean()}")
  print(f"Entre Alta Médica y Alta Administrativa: {dataframe['DIF_ALTA_ADMIN_MEDICA'].mean()}")
  print(f"Entre Ingreso y Alta Administrativa: {dataframe['ESTADIA_TOTAL'].mean()}")
  print(f"="*85)
#  print(f"Mediana de tiempo entre Alta Médica e Ingreso: {dataframe['DIF_ALTA_MEDICA_INGRESO'].median()}")
#  print(f"Mediana de tiempo entre Alta administrativa e Ingreso: {dataframe['ESTADIA_TOTAL'].median()}")
#  print(f"Mediana de tiempo entre Alta administrativa y Alta médica: {dataframe['DIF_ALTA_ADMIN_MEDICA'].median()}")

  secciones = dataframe['SECCION'].unique()
  for i, secc in enumerate(secciones):
    secc_temp = pd.DataFrame(dataframe[dataframe['SECCION']==secciones[i]])
    print(f'\nMedias de tiempo según estado del paciente en {secc}:')
    print(f"="*85)
    print(f"Entre Ingreso y Alta Médica en {secc}: {secc_temp['DIF_ALTA_MEDICA_INGRESO'].mean()}")
    print(f"Entre Alta Médica y Alta Administrativa en {secc}: {secc_temp['DIF_ALTA_ADMIN_MEDICA'].mean()}")
    print(f"Entre Ingreso y Alta Administrativa en {secc}: {secc_temp['ESTADIA_TOTAL'].mean()}")
    print(f"="*85)
#    print(f"Mediana de tiempo entre Alta Médica e Ingreso en {secc}: {secc_temp['DIF_ALTA_MEDICA_INGRESO'].median()}")
#    print(f"Mediana de tiempo entre Alta administrativa e Ingreso en {secc}: {secc_temp['ESTADIA_TOTAL'].median()}")
#    print(f"Mediana de tiempo entre Alta administrativa y Alta médica en {secc}: {secc_temp['DIF_ALTA_ADMIN_MEDICA'].median()}")

def preprocess_ambulatorio(path):
  """
  Function that preprocesses 'ambulatorio' csv from Pentaho.
  
  Args:
    path (str): Path to csv to preprocess

  Returns:
    Preprocessed pandas dataframe
  """
  # Read csv
  df = pd.read_csv(path)

  # Get rid of unnecessary columns
  df = df.drop(columns=['Unnamed: 15'])

  # Get rid of unnecessary rows
  df = df.drop(range(0,4))

  # Set definitive columns
  columns = ['DNI', 'NHC', 'PACIENTE', 'SEXO', 'EDAD', 'FECHA_TURNO', 
             'HORA_TURNO', 'SERVICIO', 'SECCION', 'PRESTACION', 'AGENDA', 
             'MOTIVO_ALTA', 'DIAGNOSTICO', 'CIE10', 'DESC_CIE10']
  df.columns=columns

  # Merge 'FECHA_TURNO' and 'HORA_TURNO', so as to convert to datetime
  df['FECHA_HORA_TURNO'] = df['FECHA_TURNO'] + ' ' + df['HORA_TURNO']

  # Convert dates to datetype format
  df['FECHA_HORA_TURNO'] = pd.to_datetime(df['FECHA_HORA_TURNO'], dayfirst=True)

  # Drop 'FECHA_TURNO' and 'HORA_TURNO'
  df = df.drop(columns=['FECHA_TURNO','HORA_TURNO'])

  # Reorder columns
  columns = ['DNI', 'NHC', 'PACIENTE', 'SEXO', 'EDAD', 'FECHA_HORA_TURNO',
          'SERVICIO', 'SECCION', 'PRESTACION', 'AGENDA', 
          'MOTIVO_ALTA', 'DIAGNOSTICO', 'CIE10', 'DESC_CIE10']
  df = df[columns]

  # Sort by 'AGENDA', then 'FECHA_TURNO', then 'HORA_TURNO'
  df.sort_values(by=['SERVICIO', 'SECCION', 'FECHA_HORA_TURNO'], inplace=True)

  # Convert numerical srt values to int
  df['EDAD'] = df['EDAD'].astype(int)
#  df['DNI'] = df['DNI'].astype(int)
#  df['NHC'] = df['NHC'].astype(int)

  # Reset index
  df.reset_index(drop=True, inplace=True)
  return df

def atenciones(dataframe, por_servicio=True, por_seccion=False, torta=False, barra=True):
  """
  Function that generates statistics from emergency dataframe

  Args:
    dataframe: pandas dataframe

  Returns:

  """
  ### Atenciones por sección

  if por_servicio:
    # Create dataframe with all servicios
    df = pd.DataFrame(dataframe['SERVICIO'].value_counts(dropna=False))
    # Calculate % of total
    df['%'] = df.iloc[:,0]/df['SERVICIO'].sum()*100
    # Reset indexes
    df = df.reset_index()
    # Rename columns
    df.columns=['SERVICIO','CANTIDADES','% TOTAL']
    print(f"Atenciones por servicio (Total = {df['CANTIDADES'].sum()})\n")
    display(df)
    print('\n\n')

    if torta:
      # Plot pie
      explode_values = np.arange(0,len(df['SERVICIO'])/10,0.1)
      explode = explode_values
      df_bar = df.set_index('SERVICIO') #change index for plotting SERVICIOS not numbers
      plt.figure()
      ax = df_bar.plot(kind='pie', y='CANTIDADES', figsize=(15,10), fontsize=13, autopct="%0.2f%%", explode=explode, legend=False)
      ax.set_title(f"Atenciones por servicio (Total = {df_bar['CANTIDADES'].sum()})",fontsize=20)

    if barra:
      # Plot bar
      plt.figure()
      ax = df.plot.bar('SERVICIO','CANTIDADES',rot=45, figsize=(20,15), fontsize=18)
      plt.title(f"Atenciones por servicio (Total = {df['CANTIDADES'].sum()})", fontsize=20)
      for i in ax.patches:
        ax.text(i.get_x(), i.get_height()*1.01, str(int(i.get_height())), fontsize=13, color='dimgrey')

  if por_seccion:
    # Get all servicios
    servicios = dataframe['SERVICIO'].unique()
    for i, secc in enumerate(servicios):
      # Create dataframe with only servicios[i]
      df = pd.DataFrame(dataframe[dataframe['SERVICIO']==servicios[i]])
      # Create dataframe with value counts of servicios[i]
      df = pd.DataFrame(df['SECCION'].value_counts(dropna=False))
      # Reset indexes
      df = df.reset_index()
      # Set columns names
      df.columns=['SECCION','CANTIDADES']
      print(f"Atenciones en {servicios[i]} (Total = {df['CANTIDADES'].sum()})\n")
      display(df)
      print('\n\n')

      if torta:
        # Plot pie
        explode_values = np.arange(0,len(df['SECCION'])/10,0.1)
        explode = explode_values
        df_bar = df.set_index('SECCION') #change index for plotting SERVICIOS not numbers
        plt.figure()
        ax = df_bar.plot(kind='pie', y='CANTIDADES', figsize=(15,10), fontsize=13, autopct="%0.2f%%", explode=explode, legend=False)
        ax.set_title(f"Atenciones en {servicios[i]} (Total = {df_bar['CANTIDADES'].sum()})",fontsize=20)

      if barra:
        # Plot bar
        plt.figure()
        ax = df.plot.bar('SECCION','CANTIDADES', rot=45, figsize=(20,15), fontsize=18)
        plt.title(f"Atenciones en {servicios[i]} (Total = {df['CANTIDADES'].sum()})", fontsize=20)
        for i in ax.patches:
          ax.text(i.get_x(), i.get_height()*1.01, str(int(i.get_height())), fontsize=13, color='dimgrey')
    
def top_20_cod_diagnostics_ambulatorio(dataframe, por_servicio=False, por_seccion=False):
  # Get year and months from dataframe
  year = pd.DatetimeIndex(dataframe['FECHA_HORA_TURNO']).year.unique()[0]
  months = pd.DatetimeIndex(dataframe['FECHA_HORA_TURNO']).month.unique()

  sin_cod = dataframe['CIE10'].isna().sum()
  total_atenciones = len(dataframe.CIE10)

  plt.figure()
  ax = dataframe['CIE10'].value_counts()[:20].plot(kind="bar", figsize=(15,10), fontsize=13, color="brown")
  ax.set_title(f"Top 20 diagnósticos codificados con CIE10 en mes(es) {months[0]} a {months[-1]} de {year}\nDiagnósticos sin codificar: {sin_cod} | Diagnósticos totales: {total_atenciones}", fontsize=20)
  plt.xticks(rotation=0)
  
  # Write totals in plot
  for i in ax.patches:
    ax.text(i.get_x(), i.get_height()*1.01, str(int(i.get_height())), fontsize=13, color='dimgrey')
  
  if por_seccion:
    # By seccion
    secciones = dataframe['SECCION'].unique()
    for i, secc in enumerate(secciones):
      secc_temp = pd.DataFrame(dataframe[dataframe['SECCION']==secciones[i]])
      sin_cod_temp = secc_temp['CIE10'].isna().sum()
      total_atenciones_temp = len(secc_temp.CIE10)

      if len(secc_temp['CIE10'].value_counts(dropna=False)) > 1:
        plt.figure()
        ax = secc_temp['CIE10'].value_counts()[:20].plot(kind="bar", figsize=(15,10), fontsize=13, color="brown")
        ax.set_title(f"Top 20 diagnósticos codificados con CIE10 en {secc} en mes(es) {months[0]} a {months[-1]} de {year}\nDiagnósticos sin codificar: {sin_cod_temp} | Diagnósticos totales: {total_atenciones_temp}", fontsize=20)
        plt.xticks(rotation=0)

        # Write totals in plot
        for i in ax.patches:
          ax.text(i.get_x(), i.get_height()*1.01, str(int(i.get_height())), fontsize=13, color='dimgrey')
      
      else:
        plt.figure()
        ax = secc_temp['CIE10'].value_counts(dropna=False).plot(kind="bar", figsize=(15,10), fontsize=13, color="brown")
        ax.set_title(f"Top 20 diagnósticos codificados con CIE10 en {secc} en mes(es) {months[0]} a {months[-1]} de {year}\nDiagnósticos sin codificar: {sin_cod_temp} | Diagnósticos totales: {total_atenciones_temp}", fontsize=20)
        plt.xticks(rotation=0);
        # Write totals in plot
        for i in ax.patches:
          ax.text(i.get_x(), i.get_height()*1.01, str(int(i.get_height())), fontsize=13, color='dimgrey')

  if por_servicio:  
    # By service
    servicios = dataframe['SERVICIO'].unique()
    for i, serv in enumerate(servicios):
      serv_temp = pd.DataFrame(dataframe[dataframe['SERVICIO']==servicios[i]])
      sin_cod_temp = serv_temp['CIE10'].isna().sum()
      total_atenciones_temp = len(serv_temp.CIE10)

      if len(serv_temp['CIE10'].value_counts(dropna=False)) > 1:
        plt.figure()
        ax = serv_temp['CIE10'].value_counts()[:20].plot(kind="bar", figsize=(15,10), fontsize=13, color="brown")
        ax.set_title(f"Top 20 diagnósticos codificados con CIE10 en {serv} en mes(es) {months[0]} a {months[-1]} de {year}\nDiagnósticos sin codificar: {sin_cod_temp} | Diagnósticos totales: {total_atenciones_temp}", fontsize=20)
        plt.xticks(rotation=0)
        # Write totals in plot
        for i in ax.patches:
          ax.text(i.get_x(), i.get_height()*1.01, str(int(i.get_height())), fontsize=13, color='dimgrey')

      else:
        plt.figure()
        ax = serv_temp['CIE10'].value_counts(dropna=False).plot(kind="bar", figsize=(15,10), fontsize=13, color="brown")
        ax.set_title(f"Top 20 diagnósticos codificados con CIE10 en {serv} en mes(es) {months[0]} a {months[-1]} de {year}\nDiagnósticos sin codificar: {sin_cod_temp} | Diagnósticos totales: {total_atenciones_temp}", fontsize=20)
        plt.xticks(rotation=0)
        # Write totals in plot
        for i in ax.patches:
          ax.text(i.get_x(), i.get_height()*1.01, str(int(i.get_height())), fontsize=13, color='dimgrey')
          
def atenciones_por_hora_ambulatorio(dataframe, por_servicio=False):
  # Get year and months from dataframe
  year = pd.DatetimeIndex(dataframe['FECHA_HORA_TURNO']).year.unique()[0]
  months = pd.DatetimeIndex(dataframe['FECHA_HORA_TURNO']).month.unique()

  df_horas = dataframe.FECHA_HORA_TURNO.dt.hour.value_counts()
  df_horas = df_horas.sort_index()

  # Plot total
  plt.figure()
  ax = df_horas.plot(kind='bar', fontsize=13, figsize=(15,10), color="orange")
  ax.set_title(f"Cantidad de atenciones según la hora | TOTAL | AMBULATORIO | mes(es) {months[0]} a {months[-1]} de {year}")
  ax.set_ylabel("Atenciones")
  plt.xticks(rotation=0)

  for i in ax.patches:
    if i.get_height() < 1000:
      ax.text(i.get_x(), i.get_height()*1.02, str(int(i.get_height())), fontsize=13, color='dimgrey')
    else:
      ax.text(i.get_x(), i.get_height()*1.01, str(int(i.get_height())), fontsize=13, color='dimgrey')

  if por_servicio:
    servicios = dataframe['SERVICIO'].unique()

    # Loop plot by seccion
    for i, serv in enumerate(servicios):
      serv_temp = pd.DataFrame(dataframe[dataframe['SERVICIO']==servicios[i]])
      df_horas_temp = serv_temp.FECHA_HORA_TURNO.dt.hour.value_counts()
      df_horas_temp = df_horas_temp.sort_index()

      # Plot
      plt.figure()
      ax = df_horas_temp.plot(kind='bar', fontsize=13, figsize=(15,10), color="orange")
      ax.set_title(f"Cantidad de atenciones según la hora | {serv} | AMBULATORIO | mes(es) {months[0]} a {months[-1]} de {year}")
      ax.set_ylabel("Atenciones")
      plt.xticks(rotation=0)

      for i in ax.patches:
        if i.get_height() < 1000:
          ax.text(i.get_x(), i.get_height()*1.02, str(int(i.get_height())), fontsize=13, color='dimgrey')
        else:
          ax.text(i.get_x(), i.get_height()*1.01, str(int(i.get_height())), fontsize=13, color='dimgrey')
          
def atenciones_por_dia_semana_ambulatorio(dataframe, por_servicio=False):
  # Get months and year of dataframe
  year = pd.DatetimeIndex(dataframe['FECHA_HORA_TURNO']).year.unique()[0]
  months = pd.DatetimeIndex(dataframe['FECHA_HORA_TURNO']).month.unique()

  # Df prepare
  df_dias = dataframe['FECHA_HORA_TURNO'].dt.dayofweek.value_counts()
  df_dias.sort_index(inplace=True)
  df_dias = df_dias.rename({0:'Lunes', 1:'Martes', 2:'Miércoles', 3:'Jueves', 4:'Viernes', 5:'Sábado', 6:'Domingo'})

  # Plot
  plt.figure()
  ax = df_dias.plot(kind='bar', fontsize=13, figsize=(15,10), colormap="jet")
  ax.set_title(f"Cantidad de atenciones en todos los servicios por día de la semana en mes(es) {months[0]} a {months[-1]} de {year}")
  ax.set_ylabel("Atenciones")
  plt.xticks(rotation=0)
  for i in ax.patches:
    ax.text(i.get_x(), i.get_height()*1.02, str(int(i.get_height())), fontsize=13, color='dimgrey')

  # Df by seccion
  if por_servicio:
    servicios = dataframe['SERVICIO'].unique()

    for i, serv in enumerate(servicios):
      serv_temp = pd.DataFrame(dataframe[dataframe['SERVICIO']==servicios[i]])
      df_dias = serv_temp['FECHA_HORA_TURNO'].dt.dayofweek.value_counts()
      df_dias.sort_index(inplace=True)
      df_dias = df_dias.rename({0:'Lunes', 1:'Martes', 2:'Miércoles', 3:'Jueves', 4:'Viernes', 5:'Sábado', 6:'Domingo'})

      # Plot
      plt.figure(figsize=(15,15))
      ax = df_dias.plot(kind='bar', fontsize=13, figsize=(15,10), colormap="jet")
      ax.set_title(f"Cantidad de atenciones en {serv} por día de la semana en mes(es) {months[0]} a {months[-1]} de {year}")
      ax.set_ylabel("Atenciones")
      plt.xticks(rotation=0)
      for i in ax.patches:
        ax.text(i.get_x(), i.get_height()*1.02, str(int(i.get_height())), fontsize=13, color='dimgrey')
  
def atenciones_grupo_etareo_ambulatorio(dataframe, por_servicio=False):
  # Get months and year of dataframe
  year = pd.DatetimeIndex(dataframe['FECHA_HORA_TURNO']).year.unique()[0]
  months = pd.DatetimeIndex(dataframe['FECHA_HORA_TURNO']).month.unique()

  # Group classifier
  grupos = [0,0,0,0,0,0]
  for i in range(len(dataframe.EDAD)):
    if dataframe.EDAD[i] == 0:
      grupos[0] = grupos[0] + 1
    elif dataframe.EDAD[i] > 0 and dataframe.EDAD[i] < 14:
      grupos[1] = grupos[1] + 1
    elif dataframe.EDAD[i] > 14 and dataframe.EDAD[i] < 22:
      grupos[2] = grupos[2] + 1
    elif dataframe.EDAD[i] > 22 and dataframe.EDAD[i] < 41:
      grupos[3] = grupos[3] + 1
    elif dataframe.EDAD[i] > 41 and dataframe.EDAD[i] < 61:
      grupos[4] = grupos[4] + 1
    else:
      grupos[5] = grupos[5] + 1

  # Plot  
  plt.figure()  
  labels=['0 años', '1 a 13', '14 a 21', '22 a 40', '41 a 60', '+61']
  fig = plt.figure(figsize=(15,10))
  explode=[0.1,0.1,0.1,0,0.1,0.1]
  plt.pie(grupos, labels=labels, autopct='%1.2f%%', explode=explode)
  plt.title(f"Atenciones según grupo etáreo | AMBULATORIO | mes(es) {months[0]} a {months[-1]} de {year}");

  if por_servicio:
    # By seccion
    servicios = dataframe['SERVICIO'].unique()

    for j, serv in enumerate(servicios):
      serv_temp = pd.DataFrame(dataframe[dataframe['SERVICIO']==servicios[j]])
      serv_temp.reset_index(drop=True, inplace=True)
      grupos = [0,0,0,0,0,0]
      for k in range(len(serv_temp.EDAD)):
        if serv_temp.EDAD[k] == 0:
          grupos[0] = grupos[0] + 1
        elif serv_temp.EDAD[k] > 0 and serv_temp.EDAD[k] < 14:
          grupos[1] = grupos[1] + 1
        elif serv_temp.EDAD[k] > 14 and serv_temp.EDAD[k] < 22:
          grupos[2] = grupos[2] + 1
        elif serv_temp.EDAD[k] > 22 and serv_temp.EDAD[k] < 41:
          grupos[3] = grupos[3] + 1
        elif serv_temp.EDAD[k] > 41 and serv_temp.EDAD[k] < 61:
          grupos[4] = grupos[4] + 1
        else:
          grupos[5] = grupos[5] + 1
        
      # Plot  
      labels=['0 años', '1 a 13', '14 a 21', '22 a 40', '41 a 60', '+61']
      fig = plt.figure(figsize=(15,10))
      explode=[0.1,0.1,0.1,0,0.1,0.1]
      plt.pie(grupos, labels=labels, autopct='%1.2f%%', explode=explode)
      plt.title(f"Atenciones según grupo etáreo | {serv.upper()} | mes(es) {months[0]} a {months[-1]} de {year}")
      
def preprocess_hospitalizacion(path):
  """
  Function that preprocesses 'hospitalizacion' csv from Pentaho.
  
  Args:
    path (str): Path to csv to preprocess
  Returns:
    Preprocessed pandas dataframe
  """
  # Read csv
  df = pd.read_csv(path)

  # Get rid of unnecessary columns
  df.drop(columns=[f'Unnamed: {i}' for i in range(16,24,1)], inplace=True)
  df.drop(columns=['Unnamed: 0'], inplace=True)

  # Get rid of unnecessary rows
  df.drop(range(0,6), inplace=True)

  # Set definitive columns
  columns = ['DNI', 'NHC', 'PACIENTE', 'SEXO', 'EDAD', 'FECHA_HORA_INGRESO', 
          'SERVICIO', 'SECCION', 'ALTA_MEDICA', 'MOTIVO_ALTA', 'ALTA_ADMIN', 
          'PROFESIONAL', 'DIAGNOSTICO_LIBRE', 'CIE10', 'DESC_CIE10']
  df.columns=columns

  # Convert dates to datetype format
  df['ALTA_ADMIN'] = pd.to_datetime(df['ALTA_ADMIN'], dayfirst=True)
  df['ALTA_MEDICA'] = pd.to_datetime(df['ALTA_MEDICA'], dayfirst=True)
  df['FECHA_HORA_INGRESO'] = pd.to_datetime(df['FECHA_HORA_INGRESO'], dayfirst=True)

  # Create time difference columns
  df['DIF_ALTA_ADMIN_MEDICA'] = df['ALTA_ADMIN'] - df['ALTA_MEDICA']
  df['DIF_ALTA_MEDICA_INGRESO'] = df['ALTA_MEDICA'] - df['FECHA_HORA_INGRESO']
  df['ESTADIA_TOTAL'] = df['ALTA_ADMIN'] - df['FECHA_HORA_INGRESO']

  # Sort by 'FECHA_HORA_INGRESO'
  df.sort_values(by=['FECHA_HORA_INGRESO', 'SERVICIO'], inplace=True)

  # Convert numerical srt values to int
  df['EDAD'] = df['EDAD'].astype(int)
#  df['DNI'] = df['DNI'].astype(int)
#  df['NHC'] = df['NHC'].astype(int)

  # Reset index
  df.reset_index(drop=True, inplace=True)
  return df

def atenciones_hosp(dataframe):
  # Defino los dos servicios principales
  toco = dataframe[dataframe['SERVICIO']=='Tocoginecología']
  neo = dataframe[dataframe['SERVICIO']=='Neonatología']
  # Genero df's con totales
  toco_df = pd.DataFrame({'ATENCIONES':toco['SECCION'].value_counts(),
                          '% TOTAL':np.round(toco['SECCION'].value_counts(normalize=True)*100,2)})
  neo_df = pd.DataFrame({'ATENCIONES':neo['SECCION'].value_counts(),
                         '% TOTAL':np.round(neo['SECCION'].value_counts(normalize=True)*100,2)})
  print(f'Atenciones en Tocoginecología | HOSPITALIZACIÓN (Total = {toco_df.ATENCIONES.sum()})')
  display(toco_df)
  print('\n')
  print(f'Atenciones en Neonatología | HOSPITALIZACIÓN (Total = {neo_df.ATENCIONES.sum()})')
  display(neo_df)
  print('\n')

  # Plot
  fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(20,20))
  toco_df.ATENCIONES.plot.bar(rot=45, ax=ax1)
  neo_df.ATENCIONES.plot.bar(rot=45, ax=ax2)
  toco_df.plot.pie(y='ATENCIONES',
                   ax=ax3,
                   autopct="%.2f")
  neo_df.plot.pie(y='ATENCIONES',
                  ax=ax4,
                  autopct="%.2f")
  ax1.set_title(f'Atenciones en Tocoginecología | HOSPITALIZACIÓN (Total = {toco_df.ATENCIONES.sum()})')
  ax2.set_title(f'Atenciones en Neonatología | HOSPITALIZACIÓN (Total = {neo_df.ATENCIONES.sum()})')
  ax3.set_title(f'Atenciones en Tocoginecología | HOSPITALIZACIÓN (Total = {toco_df.ATENCIONES.sum()})')
  ax4.set_title(f'Atenciones en Neonatología | HOSPITALIZACIÓN (Total = {neo_df.ATENCIONES.sum()})')
  for i in ax1.patches:
    ax1.text(i.get_x(), i.get_height()*1.02, str(int(i.get_height())), fontsize=13, color='dimgrey')
  for i in ax2.patches:
    ax2.text(i.get_x(), i.get_height()*1.02, str(int(i.get_height())), fontsize=13, color='dimgrey')
    
def top_20_professionals_hosp(dataframe):
  # Get year and months from dataframe
  year = dataframe.FECHA_HORA_INGRESO.dt.year.unique()[0]
  months = dataframe.FECHA_HORA_INGRESO.dt.month.unique()

  # Defino los dos servicios principales
  toco = dataframe[dataframe['SERVICIO']=='Tocoginecología']
  neo = dataframe[dataframe['SERVICIO']=='Neonatología']

  # Me quedo con las columnas que quiero solamente
  toco_df = pd.DataFrame({'ATENCIONES':toco['PROFESIONAL'].value_counts(),
                          '% TOTAL':np.round(toco['PROFESIONAL'].value_counts(normalize=True)*100,2)})
  neo_df = pd.DataFrame({'ATENCIONES':neo['PROFESIONAL'].value_counts(),
                          'SECCION':np.round(neo['PROFESIONAL'].value_counts(normalize=True)*100,2)})
  print(f'Top 20 profesionales con más atenciones en Tocoginecología\nHOSPITALIZACIÓN | mes(es) {months[0]} a {months[-1]} de {year}')
  display(toco_df[:20])
  print('\n\n')
  print(f'Top 20 profesionales con más atenciones en Neonatología\nHOSPITALIZACIÓN | mes(es) {months[0]} a {months[-1]} de {year}')
  display(neo_df[:20])

  # Graficamos con totales
  fig, ((ax1, ax2)) = plt.subplots(2,1, figsize=(20,20))
  toco_df.ATENCIONES[:20].plot.bar(rot=45, ax=ax1)
  neo_df.ATENCIONES[:20].plot.bar(rot=45, ax=ax2)
  ax1.set_title(f'Top 20 profesionales con más atenciones en Tocoginecología (Total = {toco_df.ATENCIONES.sum()})\nHOSPITALIZACIÓN | mes(es) {months[0]} a {months[-1]} de {year}')
  ax2.set_title(f'Top 20 profesionales con más atenciones en Neonatología (Total = {neo_df.ATENCIONES.sum()})\nHOSPITALIZACIÓN | mes(es) {months[0]} a {months[-1]} de {year}')
  for i in ax1.patches:
    ax1.text(i.get_x(), i.get_height()*1.02, str(int(i.get_height())), fontsize=13, color='dimgrey')
  for i in ax2.patches:
    ax2.text(i.get_x(), i.get_height()*1.02, str(int(i.get_height())), fontsize=13, color='dimgrey')
    
def atenciones_por_hora_hosp(dataframe, por_servicio=False):
  # Get year and months from dataframe
  year = dataframe.FECHA_HORA_INGRESO.dt.year.unique()[0]
  months = dataframe.FECHA_HORA_INGRESO.dt.month.unique()

  df_horas = pd.DataFrame({'ATENCIONES':dataframe.FECHA_HORA_INGRESO.dt.hour.value_counts()})
  df_horas = df_horas.sort_index()
  #print('Atenciones por hora | HOSPITALIZACIÓN')
  #display(df_horas)

  # Plot
  fig, ax = plt.subplots(figsize=(12,12))
  df_horas.plot.bar(rot=0, ax=ax)
  ax.set_title(f'Atenciones por hora | HOSPITALIZACIÓN | mes(es) {months[0]} a {months[-1]} de {year}')
  for i in ax.patches:
    ax.text(i.get_x(), i.get_height()*1.02, str(int(i.get_height())), fontsize=11, color='dimgrey')
  
  if por_servicio:
    secciones = dataframe['SECCION'].unique()

    # Loop plot by seccion
    for i, secc in enumerate(secciones):
      secc_temp = pd.DataFrame(dataframe[dataframe['SECCION']==secciones[i]])
      df_horas_temp = secc_temp.FECHA_HORA_INGRESO.dt.hour.value_counts()
      df_horas_temp = df_horas_temp.sort_index()

      # Plot
      plt.figure()
      ax = df_horas_temp.plot(kind='bar', fontsize=13, figsize=(12,12), color="orange")
      ax.set_title(f"Cantidad de atenciones según la hora | {secc} | HOSPITALIZACIÓN | mes(es) {months[0]} a {months[-1]} de {year}")
      ax.set_ylabel("Atenciones")
      plt.xticks(rotation=0)

      for i in ax.patches:
        if i.get_height() < 1000:
          ax.text(i.get_x(), i.get_height()*1.02, str(int(i.get_height())), fontsize=13, color='dimgrey')
        else:
          ax.text(i.get_x(), i.get_height()*1.01, str(int(i.get_height())), fontsize=13, color='dimgrey')
   
def preprocess_cirugias(path):
  cirugias = pd.read_excel(path)
  cirugias = cirugias.drop(index=[0,1,2,3])
  cirugias.columns=['FECHA', 'SOLICITADAS', 'CONFIRMADAS', 'REALIZADAS', 'CANCELADAS']
  cirugias.FECHA = pd.to_datetime(cirugias.FECHA, dayfirst=True)
  cirugias = cirugias.sort_values(by='FECHA')
  cirugias = cirugias.set_index('FECHA')
  return cirugias

def cirugias_plot(dataframe):
  year = dataframe.index.year.unique()[0]
  months = dataframe.index.month.unique()

  # line
  fig, (ax1,ax2) = plt.subplots(2,1, figsize=(20,15))
  dataframe.plot(x_compat=True, ax=ax1)
  ax1.set_title(f'Cirugías en mes(es) {months[0]} a {months[-1]} de {year}')
  # bar
  dataframe.sum().plot.bar(rot=0, ax=ax2)
  ax2.set_title(f'Cirugías en mes(es) {months[0]} a {months[-1]} de {year}')
  for i in ax2.patches:
    ax2.text(i.get_x(), i.get_height()*1.02, str(int(i.get_height())), fontsize=13, color='dimgrey')

def preprocess_lab(path):
  lab = pd.read_csv(path)
  lab = lab.drop(index=[0,1,2,3,4,5])
  lab = lab.drop(columns=['Unnamed: 7','Unnamed: 8','Unnamed: 9','Unnamed: 10','Unnamed: 11','Unnamed: 12','Unnamed: 13','Unnamed: 14','Unnamed: 15'])
  lab.columns=['PETICION','PRUEBA','FECHA','HC','DNI','PACIENTE','AMBITO']
  lab['FECHA'] = pd.to_datetime(lab['FECHA'], dayfirst=True)
  lab = lab.sort_values(by='FECHA')
  lab = lab.reset_index(drop=True)
  return lab
    
def labo_all(dataframe):
  # Useful data
  total_tipo_pruebas = dataframe.PRUEBA.unique().shape[0]
  total_pacientes = dataframe.PACIENTE.unique().shape[0]
  total_pruebas = dataframe.index[-1] + 1
  year = pd.DatetimeIndex(dataframe['FECHA']).year.unique()[0] 
  months = pd.DatetimeIndex(dataframe['FECHA']).month.unique()

  # Plot pruebas
  fig, ax = plt.subplots(figsize=(15,7))
  dataframe.PRUEBA.value_counts()[:30].plot.bar(ax=ax)
  ax.set_title(f'Peticiones realizadas en mes(es) {months[0]} a {months[-1]} de {year}\n Total de pruebas: {total_pruebas}\nTotal tipo de pruebas: {total_tipo_pruebas}')
  ax.set_xlabel('Pruebas')
  ax.set_ylabel('Cantidad de peticiones')  
  for i in ax.patches:
    if i.get_height() < 1000:
      ax.text(i.get_x(), i.get_height()*1.03, str(int(i.get_height())), fontsize=10, color='dimgrey')
    else:
      ax.text(i.get_x(), i.get_height()*1.01, str(int(i.get_height())), fontsize=10, color='dimgrey')  

  # Plot hours
  fig, ax = plt.subplots(figsize=(10,7))
  df_hours = lab.FECHA.dt.hour.value_counts()
  df_hours = df_hours.sort_index()
  df_hours.plot.bar(rot=0, ax=ax);
  ax.set_title(f'Peticiones realizadas por hora en mes(es) {months[0]} a {months[-1]} de {year}\n Total de pruebas: {total_pruebas}\nTotal tipo de pruebas: {total_tipo_pruebas}')
  ax.set_xlabel('HORAS')
  ax.set_ylabel('Cantidad de peticiones')  
  for i in ax.patches:
    if i.get_height() < 1000:
      ax.text(i.get_x(), i.get_height()*1.03, str(int(i.get_height())), fontsize=10, color='dimgrey')
    else:
      ax.text(i.get_x(), i.get_height()*1.01, str(int(i.get_height())), fontsize=10, color='dimgrey')

  # Plot days
  df_days = pd.DataFrame({'DIAS':['Lunes','Martes','Miercoles','Jueves','Viernes','Sabado','Domingo'],
                        'PRUEBAS':dataframe.FECHA.dt.dayofweek.value_counts().sort_index()})
  df_days = df_days.set_index('DIAS')
  fig, ax = plt.subplots(figsize=(10,7))
  df_days.plot.bar(rot=0, ax=ax)
  ax.set_title(f'Peticiones realizadas por día en mes(es) {months[0]} a {months[-1]} de {year}\n Total de pruebas: {total_pruebas}\nTotal tipo de pruebas: {total_tipo_pruebas}')
  ax.set_xlabel('DIAS')
  ax.set_ylabel('Cantidad de peticiones')
  for i in ax.patches:
    if i.get_height() < 1000:
      ax.text(i.get_x(), i.get_height()*1.03, str(int(i.get_height())), fontsize=10, color='dimgrey')
    else:
      ax.text(i.get_x(), i.get_height()*1.01, str(int(i.get_height())), fontsize=10, color='dimgrey')
  
  # Plot months
  df_months = pd.Series(dataframe.FECHA.dt.month.value_counts().sort_index(), name='PRUEBAS')
  fig, ax = plt.subplots(figsize=(10,7))
  df_months.plot.bar(rot=0, ax=ax)
  ax.set_title(f'Peticiones realizadas por mes en mes(es) {months[0]} a {months[-1]} de {year}\n Total de pruebas: {total_pruebas}\nTotal tipo de pruebas: {total_tipo_pruebas}')
  ax.set_xlabel('MESES')
  ax.set_ylabel('Cantidad de peticiones')
  for i in ax.patches:
    if i.get_height() < 1000:
      ax.text(i.get_x(), i.get_height()*1.03, str(int(i.get_height())), fontsize=10, color='dimgrey')
    else:
      ax.text(i.get_x(), i.get_height()*1.01, str(int(i.get_height())), fontsize=10, color='dimgrey')  
  
  # Plot ámbito
  fig, ax = plt.subplots(figsize=(10,7))
  dataframe.AMBITO.value_counts().plot.bar(rot=0, ax=ax)
  ax.set_title(f'Peticiones realizadas por sector en mes(es) {months[0]} a {months[-1]} de {year}\n Total de pruebas: {total_pruebas}\nTotal tipo de pruebas: {total_tipo_pruebas}')
  ax.set_xlabel('SECTORES')
  ax.set_ylabel('Cantidad de peticiones')  
  for i in ax.patches:
    if i.get_height() < 1000:
      ax.text(i.get_x(), i.get_height()*1.03, str(int(i.get_height())), fontsize=10, color='dimgrey')
    else:
      ax.text(i.get_x(), i.get_height()*1.01, str(int(i.get_height())), fontsize=10, color='dimgrey')       
