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
  

 def top_20_professionals(dataframe):
  secciones = dataframe['SECCION'].unique()
  # Dataframe loop
  for i, secc in enumerate(secciones):
    secc_temp = pd.DataFrame(dataframe[dataframe['SECCION']==secciones[i]])
    professional_vc = secc_temp['PROFESIONAL'].value_counts(dropna=False)[:20]
    professional = pd.DataFrame(secc_temp['PROFESIONAL'].value_counts(dropna=False))[:20]
    professional = professional.reset_index()
    professional.columns=['PROFESIONAL','ATENCIONES']
    print(f'Top 20 profesionales en atenciones de {secc}')
    display(professional)
    print('\n\n')
    
    # Graficamos con totales
    ax = professional.plot(kind='bar', figsize=(20,10), fontsize=12)
    ax.set_title(f"Top 20 profesionales en atenciones de {secc}")
    ax.set_ylabel("Cantidad de atenciones")
    plt.xticks(rotation=70)

    #for i in ax.patches:
    #  ax.text(i.get_x(), i.get_height() + 15, str(i.get_height()), fontsize=13, color='dimgrey')
  
 def atenciones_por_hora(dataframe):
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
      ax.text(i.get_x() - 0.1, i.get_height() + 12, str(int(i.get_height())), fontsize=13, color='dimgrey')
    else:
      ax.text(i.get_x() - 0.21, i.get_height() + 12, str(int(i.get_height())), fontsize=13, color='dimgrey')

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

#    for i in ax.patches:
#      if i.get_height() < 1000:
#        ax.text(i.get_x() - 0.1, i.get_height() + 12, str(int(i.get_height())), fontsize=13, color='dimgrey')
#      else:
#        ax.text(i.get_x() - 0.21, i.get_height() + 12, str(int(i.get_height())), fontsize=13, color='dimgrey')


def atenciones_por_dia_semana(dataframe):
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
  for i in ax.patches:
    ax.text(i.get_x() + 0.1, i.get_height() + 12, str(int(i.get_height())), fontsize=13, color='dimgrey')

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
#    for i in ax.patches:
#      ax.text(i.get_x() + 0.1, i.get_height() + 12, str(int(i.get_height())), fontsize=13, color='dimgrey')


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
    secc_temp['EDAD'] = secc_temp['EDAD'].astype(int)
    print(secc_temp['EDAD'])
    grupos = [0,0,0,0,0,0]
    for k in range(len(secc_temp.EDAD)):
      if secc_temp.EDAD[i] == 0:
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
    plt.title(f"Atenciones en {secc} según grupo etáreo | GUARDIA");

    
def motivo_alta(dataframe):
  dataframe['MOTIVO_ALTA'].value_counts(dropna=False)
  ax = dataframe['MOTIVO_ALTA'].value_counts(dropna=False).plot(kind='barh', figsize=(15,10))
  ax.set_title("Motivo de alta")

  for i in ax.patches:
    if i.get_width() > 1000:
      ax.text(i.get_width() - 600, i.get_y() + 0.20, str(i.get_width()), fontsize=13, color='white')
    else:
      ax.text(i.get_width() + 20, i.get_y() + .20, str(i.get_width()), fontsize=13, color='black')
 

def top_20_cod_diagnostics(dataframe):
  sin_cod = dataframe['CIE10'].value_counts(dropna=False)[0]
  total_atenciones = dataframe.CIE10.shape

  plt.figure()
  ax = dataframe['CIE10'].value_counts(dropna=False)[1:21].plot(kind="bar", figsize=(15,10), fontsize=13, color="brown")
  ax.set_title("Top 20 diagnósticos codificados con CIE10")
  plt.xticks(rotation=0)
  print(f'Nota: el número de diagnósticos sin codificar es: {sin_cod}')
  print(f'Nota: el número de diagnósticos total es: {total_atenciones}')

  for i in ax.patches:
    if i.get_height() < 100:
      ax.text(i.get_x() + 0.1, i.get_height() + 2, str(i.get_height()), fontsize=13)
    else:
      ax.text(i.get_x() - 0.05, i.get_height() + 2, str(i.get_height()), fontsize=13)
  
  # By seccion
  secciones = dataframe['SECCION'].unique()
  for i, secc in enumerate(secciones):
    secc_temp = pd.DataFrame(dataframe[dataframe['SECCION']==secciones[i]])
    sin_cod_temp = secc_temp['CIE10'].value_counts(dropna=False)[0]
    total_atenciones_temp = secc_temp.CIE10.shape

    plt.figure()
    ax = secc_temp['CIE10'].value_counts(dropna=False)[1:21].plot(kind="bar", figsize=(15,10), fontsize=13, color="brown")
    ax.set_title(f"Top 20 diagnósticos en {secc} codificados con CIE10")
    plt.xticks(rotation=0)
    print(f'Nota: el número de diagnósticos sin codificar en {secc} es: {sin_cod_temp}')
    print(f'Nota: el número de diagnósticos total en {secc} es: {total_atenciones_temp}')
 

def medias_tiempo(dataframe):
  print('Medias de tiempo según estado del paciente:')
  print(f"="*85)
  print(f"Media de tiempo entre Alta Médica e Ingreso: {dataframe['DIF_ALTA_MEDICA_INGRESO'].mean()}")
  print(f"Media de tiempo entre Alta administrativa e Ingreso: {dataframe['ESTADIA_TOTAL'].mean()}")
  print(f"Media de tiempo entre Alta administrativa y Alta médica: {dataframe['DIF_ALTA_ADMIN_MEDICA'].mean()}")
  print(f"="*85)
  print(f"Mediana de tiempo entre Alta Médica e Ingreso: {dataframe['DIF_ALTA_MEDICA_INGRESO'].median()}")
  print(f"Mediana de tiempo entre Alta administrativa e Ingreso: {dataframe['ESTADIA_TOTAL'].median()}")
  print(f"Mediana de tiempo entre Alta administrativa y Alta médica: {dataframe['DIF_ALTA_ADMIN_MEDICA'].median()}")

  secciones = dataframe['SECCION'].unique()
  for i, secc in enumerate(secciones):
    secc_temp = pd.DataFrame(dataframe[dataframe['SECCION']==secciones[i]])
    print(f'\nMedias de tiempo según estado del paciente  en {secc}:')
    print(f"="*85)
    print(f"Media de tiempo entre Alta Médica e Ingreso en {secc}: {secc_temp['DIF_ALTA_MEDICA_INGRESO'].mean()}")
    print(f"Media de tiempo entre Alta administrativa e Ingreso en {secc}: {secc_temp['ESTADIA_TOTAL'].mean()}")
    print(f"Media de tiempo entre Alta administrativa y Alta médica en {secc}: {secc_temp['DIF_ALTA_ADMIN_MEDICA'].mean()}")
    print(f"="*85)
    print(f"Mediana de tiempo entre Alta Médica e Ingreso en {secc}: {secc_temp['DIF_ALTA_MEDICA_INGRESO'].median()}")
    print(f"Mediana de tiempo entre Alta administrativa e Ingreso en {secc}: {secc_temp['ESTADIA_TOTAL'].median()}")
    print(f"Mediana de tiempo entre Alta administrativa y Alta médica en {secc}: {secc_temp['DIF_ALTA_ADMIN_MEDICA'].median()}")
