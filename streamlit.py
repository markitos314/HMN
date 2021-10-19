import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np
import datetime
from hmn_functions import preprocess_ambulatorio
from hmn_functions import preprocess_emergencias

def motivo_alta(dataframe):
  df_display = pd.DataFrame(dataframe['MOTIVO_ALTA'].value_counts(dropna=False))
  df_display = df_display.reset_index()
  df_display.columns=['MOTIVO_ALTA', 'CANTIDAD']

  fig, ax = plt.subplots()
  ax = dataframe['MOTIVO_ALTA'].value_counts(dropna=False).plot(kind='barh', figsize=(15,10))
  ax.set_title("Motivo de alta")

  for i in ax.patches:
    if i.get_width() > 1000:
      ax.text(i.get_width()*.9, i.get_y()*1.02, str(i.get_width()), fontsize=13, color='black')
    else:
      ax.text(i.get_width()*1.03, i.get_y()*1.02, str(i.get_width()), fontsize=13, color='black')
  return fig, df_display

def atenciones_por_dia_semana(dataframe, por_servicio=False):
  # Df prepare
  df_dias = dataframe['FECHA_HORA_TURNO'].dt.dayofweek.value_counts()
  df_dias.sort_index(inplace=True)
  df_dias = df_dias.rename({0:'Lunes', 1:'Martes', 2:'Miércoles', 3:'Jueves', 4:'Viernes', 5:'Sábado', 6:'Domingo'})

  # Plot
  fig, ax = plt.subplots()
  ax = df_dias.plot(kind='bar', fontsize=13, figsize=(15,10), colormap="jet")
  ax.set_title("Cantidad de atenciones en todos los servicios por día de la semana")
  ax.set_ylabel("Atenciones")
  plt.xticks(rotation=0)

  # Write totals
  for i in ax.patches:
    ax.text(i.get_x() + 0.1, i.get_height()*1.02, str(int(i.get_height())), fontsize=13, color='dimgrey')
  
  # Df by seccion
  # if por_servicio:
  #   servicios = dataframe['SERVICIO'].unique()

  #   for i, serv in enumerate(servicios):
  #     serv_temp = pd.DataFrame(dataframe[dataframe['SERVICIO']==servicios[i]])
  #     df_dias = serv_temp['FECHA_HORA_TURNO'].dt.dayofweek.value_counts()
  #     df_dias.sort_index(inplace=True)
  #     df_dias = df_dias.rename({0:'Lunes', 1:'Martes', 2:'Miércoles', 3:'Jueves', 4:'Viernes', 5:'Sábado', 6:'Domingo'})

  #     # Plot
  #     fig2, ax2 = plt.subplots()
  #     ax2 = df_dias.plot(kind='bar', fontsize=13, figsize=(15,10), colormap="jet")
  #     ax2.set_title(f"Cantidad de atenciones en {serv} por día de la semana en mes(es) {months[0]} a {months[-1]} de {year}")
  #     ax2.set_ylabel("Atenciones")
  #     plt.xticks(rotation=0)
  #     for i in ax2.patches:
  #       ax2.text(i.get_x(), i.get_height()*1.02, str(int(i.get_height())), fontsize=13, color='dimgrey')  
  #   return fig2

  return df_dias, fig

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
  labels=['0 años', '1 a 13', '14 a 21', '22 a 40', '41 a 60', '+61']
  explode=[0.1,0.1,0.1,0,0.1,0.1]
  edades = pd.Series(grupos,index=labels, name='Cantidad')
  fig, ax = plt.subplots()
  ax = edades.plot(kind='pie', autopct='%1.2f%%', explode=explode)
  ax.set_title(f"Atenciones según grupo etáreo | AMBULATORIO | mes(es) {months[0]} a {months[-1]} de {year}");

  # if por_servicio:
  #   # By seccion
  #   servicios = dataframe['SERVICIO'].unique()

  #   for j, serv in enumerate(servicios):
  #     serv_temp = pd.DataFrame(dataframe[dataframe['SERVICIO']==servicios[j]])
  #     serv_temp.reset_index(drop=True, inplace=True)
  #     grupos = [0,0,0,0,0,0]
  #     for k in range(len(serv_temp.EDAD)):
  #       if serv_temp.EDAD[k] == 0:
  #         grupos[0] = grupos[0] + 1
  #       elif serv_temp.EDAD[k] > 0 and serv_temp.EDAD[k] < 14:
  #         grupos[1] = grupos[1] + 1
  #       elif serv_temp.EDAD[k] > 14 and serv_temp.EDAD[k] < 22:
  #         grupos[2] = grupos[2] + 1
  #       elif serv_temp.EDAD[k] > 22 and serv_temp.EDAD[k] < 41:
  #         grupos[3] = grupos[3] + 1
  #       elif serv_temp.EDAD[k] > 41 and serv_temp.EDAD[k] < 61:
  #         grupos[4] = grupos[4] + 1
  #       else:
  #         grupos[5] = grupos[5] + 1
        
  #     # Plot  
  #     labels=['0 años', '1 a 13', '14 a 21', '22 a 40', '41 a 60', '+61']
  #     fig = plt.figure(figsize=(15,10))
  #     explode=[0.1,0.1,0.1,0,0.1,0.1]
  #     plt.pie(grupos, labels=labels, autopct='%1.2f%%', explode=explode)
  #     plt.title(f"Atenciones según grupo etáreo | {serv.upper()} | mes(es) {months[0]} a {months[-1]} de {year}")
  return fig, edades

def atenciones_por_hora_ambulatorio(dataframe, por_servicio=False):
  # Get year and months from dataframe
  year = pd.DatetimeIndex(dataframe['FECHA_HORA_TURNO']).year.unique()[0]
  months = pd.DatetimeIndex(dataframe['FECHA_HORA_TURNO']).month.unique()

  df_horas = dataframe.FECHA_HORA_TURNO.dt.hour.value_counts()
  df_horas = df_horas.sort_index()

  # Plot total
  fig, ax = plt.subplots()
  ax = df_horas.plot(kind='bar', fontsize=13, figsize=(15,10), color="orange")
  ax.set_title(f"Cantidad de atenciones según la hora | TOTAL | AMBULATORIO | mes(es) {months[0]} a {months[-1]} de {year}")
  ax.set_ylabel("Atenciones")
  plt.xticks(rotation=0)

  for i in ax.patches:
    if i.get_height() > 1000:
      ax.text(i.get_x(), i.get_height()*1.01, str(int(i.get_height())), fontsize=13, color='dimgrey')
    elif i.get_height() < 1000 and i.get_height() > 100:
      ax.text(i.get_x(), i.get_height()*1.1, str(int(i.get_height())), fontsize=13, color='dimgrey')
    else:
      ax.text(i.get_x(), i.get_height()*1.5, str(int(i.get_height())), fontsize=13, color='dimgrey')
  # if por_servicio:
  #   servicios = dataframe['SERVICIO'].unique()

  #   # Loop plot by seccion
  #   for i, serv in enumerate(servicios):
  #     serv_temp = pd.DataFrame(dataframe[dataframe['SERVICIO']==servicios[i]])
  #     df_horas_temp = serv_temp.FECHA_HORA_TURNO.dt.hour.value_counts()
  #     df_horas_temp = df_horas_temp.sort_index()

  #     # Plot
  #     plt.figure()
  #     ax = df_horas_temp.plot(kind='bar', fontsize=13, figsize=(15,10), color="orange")
  #     ax.set_title(f"Cantidad de atenciones según la hora | {serv} | AMBULATORIO | mes(es) {months[0]} a {months[-1]} de {year}")
  #     ax.set_ylabel("Atenciones")
  #     plt.xticks(rotation=0)

  #     for i in ax.patches:
  #       if i.get_height() < 1000:
  #         ax.text(i.get_x(), i.get_height()*1.02, str(int(i.get_height())), fontsize=13, color='dimgrey')
  #       else:
  #         ax.text(i.get_x(), i.get_height()*1.01, str(int(i.get_height())), fontsize=13, color='dimgrey')
  return fig, df_horas

def top_20_cod_diagnostics_ambulatorio(dataframe, por_servicio=False, por_seccion=False):
  # Get year and months from dataframe
  year = pd.DatetimeIndex(dataframe['FECHA_HORA_TURNO']).year.unique()[0]
  months = pd.DatetimeIndex(dataframe['FECHA_HORA_TURNO']).month.unique()

  sin_cod = dataframe['CIE10'].isna().sum()
  total_atenciones = len(dataframe.CIE10)

  # Plot
  fig, ax = plt.subplots()
  ax = dataframe['CIE10'].value_counts()[:20].plot(kind="bar", figsize=(15,10), fontsize=13, color="brown")
  ax.set_title(f"Top 20 diagnósticos codificados con CIE10 en mes(es) {months[0]} a {months[-1]} de {year}\nDiagnósticos sin codificar: {sin_cod} | Diagnósticos totales: {total_atenciones}", fontsize=20)
  plt.xticks(rotation=0)
  
  # Write totals in plot
  for i in ax.patches:
    ax.text(i.get_x(), i.get_height()*1.01, str(int(i.get_height())), fontsize=13, color='dimgrey')
  
  # if por_seccion:
  #   # By seccion
  #   secciones = dataframe['SECCION'].unique()
  #   for i, secc in enumerate(secciones):
  #     secc_temp = pd.DataFrame(dataframe[dataframe['SECCION']==secciones[i]])
  #     sin_cod_temp = secc_temp['CIE10'].isna().sum()
  #     total_atenciones_temp = len(secc_temp.CIE10)

  #     if len(secc_temp['CIE10'].value_counts(dropna=False)) > 1:
  #       plt.figure()
  #       ax = secc_temp['CIE10'].value_counts()[:20].plot(kind="bar", figsize=(15,10), fontsize=13, color="brown")
  #       ax.set_title(f"Top 20 diagnósticos codificados con CIE10 en {secc} en mes(es) {months[0]} a {months[-1]} de {year}\nDiagnósticos sin codificar: {sin_cod_temp} | Diagnósticos totales: {total_atenciones_temp}", fontsize=20)
  #       plt.xticks(rotation=0)

  #       # Write totals in plot
  #       for i in ax.patches:
  #         ax.text(i.get_x(), i.get_height()*1.01, str(int(i.get_height())), fontsize=13, color='dimgrey')
      
  #     else:
  #       plt.figure()
  #       ax = secc_temp['CIE10'].value_counts(dropna=False).plot(kind="bar", figsize=(15,10), fontsize=13, color="brown")
  #       ax.set_title(f"Top 20 diagnósticos codificados con CIE10 en {secc} en mes(es) {months[0]} a {months[-1]} de {year}\nDiagnósticos sin codificar: {sin_cod_temp} | Diagnósticos totales: {total_atenciones_temp}", fontsize=20)
  #       plt.xticks(rotation=0);
  #       # Write totals in plot
  #       for i in ax.patches:
  #         ax.text(i.get_x(), i.get_height()*1.01, str(int(i.get_height())), fontsize=13, color='dimgrey')

  # if por_servicio:  
  #   # By service
  #   servicios = dataframe['SERVICIO'].unique()
  #   for i, serv in enumerate(servicios):
  #     serv_temp = pd.DataFrame(dataframe[dataframe['SERVICIO']==servicios[i]])
  #     sin_cod_temp = serv_temp['CIE10'].isna().sum()
  #     total_atenciones_temp = len(serv_temp.CIE10)

  #     if len(serv_temp['CIE10'].value_counts(dropna=False)) > 1:
  #       plt.figure()
  #       ax = serv_temp['CIE10'].value_counts()[:20].plot(kind="bar", figsize=(15,10), fontsize=13, color="brown")
  #       ax.set_title(f"Top 20 diagnósticos codificados con CIE10 en {serv} en mes(es) {months[0]} a {months[-1]} de {year}\nDiagnósticos sin codificar: {sin_cod_temp} | Diagnósticos totales: {total_atenciones_temp}", fontsize=20)
  #       plt.xticks(rotation=0)
  #       # Write totals in plot
  #       for i in ax.patches:
  #         ax.text(i.get_x(), i.get_height()*1.01, str(int(i.get_height())), fontsize=13, color='dimgrey')

  #     else:
  #       plt.figure()
  #       ax = serv_temp['CIE10'].value_counts(dropna=False).plot(kind="bar", figsize=(15,10), fontsize=13, color="brown")
  #       ax.set_title(f"Top 20 diagnósticos codificados con CIE10 en {serv} en mes(es) {months[0]} a {months[-1]} de {year}\nDiagnósticos sin codificar: {sin_cod_temp} | Diagnósticos totales: {total_atenciones_temp}", fontsize=20)
  #       plt.xticks(rotation=0)
  #       # Write totals in plot
  #       for i in ax.patches:
  #         ax.text(i.get_x(), i.get_height()*1.01, str(int(i.get_height())), fontsize=13, color='dimgrey')
  return fig, dataframe

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
    st.write(f"Atenciones por servicio (Total = {df['CANTIDADES'].sum()})\n")
    st.dataframe(df)

    if torta:
      # Plot pie
      explode_values = np.arange(0,len(df['SERVICIO'])/10,0.1)
      explode = explode_values
      df_bar = df.set_index('SERVICIO') #change index for plotting SERVICIOS not numbers
      fig, ax = plt.subplots()
      ax = df_bar.plot(kind='pie',y='CANTIDADES', figsize=(15,10), fontsize=13, autopct="%0.2f%%", explode=explode, legend=False)
      ax.set_title(f"Atenciones por servicio (Total = {df_bar['CANTIDADES'].sum()})",fontsize=20)
      st.pyplot(fig)
    
    if barra:
      # Plot bar
      fig2, ax2 = plt.subplots()
      ax2 = df.plot.bar('SERVICIO', 'CANTIDADES',rot=45, figsize=(20,15), fontsize=18)
      ax2.set_title(f"Atenciones por servicio (Total = {df['CANTIDADES'].sum()})", fontsize=20)
      for i in ax2.patches:
        ax2.text(i.get_x(), i.get_height()*1.01, str(int(i.get_height())), fontsize=13, color='dimgrey')
      st.pyplot(fig2)

  # if por_seccion:
  #   # Get all servicios
  #   servicios = dataframe['SERVICIO'].unique()
  #   for i, secc in enumerate(servicios):
  #     # Create dataframe with only servicios[i]
  #     df = pd.DataFrame(dataframe[dataframe['SERVICIO']==servicios[i]])
  #     # Create dataframe with value counts of servicios[i]
  #     df = pd.DataFrame(df['SECCION'].value_counts(dropna=False))
  #     # Reset indexes
  #     df = df.reset_index()
  #     # Set columns names
  #     df.columns=['SECCION','CANTIDADES']
  #     print(f"Atenciones en {servicios[i]} (Total = {df['CANTIDADES'].sum()})\n")
  #     display(df)
  #     print('\n\n')

  #     if torta:
  #       # Plot pie
  #       explode_values = np.arange(0,len(df['SECCION'])/10,0.1)
  #       explode = explode_values
  #       df_bar = df.set_index('SECCION') #change index for plotting SERVICIOS not numbers
  #       plt.figure()
  #       ax = df_bar.plot(kind='pie', y='CANTIDADES', figsize=(15,10), fontsize=13, autopct="%0.2f%%", explode=explode, legend=False)
  #       ax.set_title(f"Atenciones en {servicios[i]} (Total = {df_bar['CANTIDADES'].sum()})",fontsize=20)

  #     if barra:
  #       # Plot bar
  #       plt.figure()
  #       ax = df.plot.bar('SECCION','CANTIDADES', rot=45, figsize=(20,15), fontsize=18)
  #       plt.title(f"Atenciones en {servicios[i]} (Total = {df['CANTIDADES'].sum()})", fontsize=20)
  #       for i in ax.patches:
  #         ax.text(i.get_x(), i.get_height()*1.01, str(int(i.get_height())), fontsize=13, color='dimgrey')


###------------------------------------------------------------------------------->Emergencias funciones<------------------------------------------------------------------------------------------
def atenciones_por_seccion(dataframe):
  """
  Function that generates statistics from emergency dataframe

  Args:
    dataframe: pandas dataframe

  Returns:

  """
  ### Atenciones por sección

  # Dataframe
  seccion = pd.DataFrame({'CANTIDADES':dataframe['SECCION'].value_counts(),
                          '% TOTAL':np.round(dataframe['SECCION'].value_counts(normalize=True)*100,2)})
  st.write(f"Atenciones por sección (Total = {seccion['CANTIDADES'].sum()})\n")

  # Plot pie
  #explode_values = np.arange(0,len(seccion)/10,0.1)
  #explode = explode_values
  fig, (ax1, ax2) = plt.subplots(2)
  ax1 = seccion.plot.pie(y='CANTIDADES',
                   autopct='%.2f%%',
                   labels=None,
                   figsize=(10,10))
  ax1.set_title(f"Atenciones por sección (Total = {seccion['CANTIDADES'].sum()})", 
                fontsize=10)
  ax1.legend(bbox_to_anchor=(1,1),
             loc='upper right',
             labels=seccion.index)

  # Plot bar
  #fig2, ax2 = plt.subplots()
  ax2 = seccion['CANTIDADES'].plot.bar(rot=45)
  ax2.set_title(f"Atenciones por sección (Total = {seccion['CANTIDADES'].sum()})", fontsize=10)
  # Wtire totals
  #for i in ax2.patches:
  #  ax2.text(i.get_x(), i.get_height()*1.01, str(int(i.get_height())), fontsize=8, color='dimgrey')

  return seccion, fig

def top_20_professionals(dataframe, por_seccion=False):
  # Prepare df
  df = pd.DataFrame({'ATENCIONES':dataframe['PROFESIONAL'].value_counts(),
                      '% TOTAL':np.round(dataframe['PROFESIONAL'].value_counts(normalize=True)*100,2)})
  #df = df.reset_index()
  #df.columns=['PROFESIONAL','ATENCIONES','% TOTAL']
  df = df.sort_values('ATENCIONES', ascending=False)
  st.write(f'Top 20 profesionales con mayoeres atenciones en todos los servicios')
  
  # Plot bar
  fig, ax = plt.subplots()
  ax = df.plot.bar(rot=45, figsize=(20,15))
  ax.set_title(f'Top 20 profesionales con mayores atenciones en todos los servicios')
  ax.set_ylabel("Cantidad de atenciones")
  ax.set_xlabel("Profesionales")

  # Write totals
  for i in ax.patches:
    ax.text(i.get_x(), i.get_height()*1.02, str(i.get_height()), fontsize=13, color='dimgrey')

  # if por_seccion:
  #   secciones = dataframe['SECCION'].unique()
  #   # Dataframe loop
  #   for i, secc in enumerate(secciones):
  #     secc_temp = pd.DataFrame(dataframe[dataframe['SECCION']==secciones[i]])
  #     professional = pd.DataFrame(secc_temp['PROFESIONAL'].value_counts(dropna=False))[:20]
  #     professional['% TOTAL'] = secc_temp['PROFESIONAL'].value_counts(dropna=False, normalize=True)*100
  #     professional = professional.reset_index()
  #     professional.columns=['PROFESIONAL','ATENCIONES', '% TOTAL']
  #     st.write(f'Top 20 profesionales en atenciones de {secc}')

  #     # Plot bar
  #     fig2, ax2 = plt.subplots()
  #     ax2 = professional.plot.bar('PROFESIONAL', 'ATENCIONES', figsize=(20,10), fontsize=12)
  #     ax2.set_title(f"Top 20 profesionales en atenciones de {secc}")
  #     ax2.set_ylabel("Cantidad de atenciones")
  #     ax2.set_xlabel("Profesionales")
  #     plt.xticks(rotation=45)

  #     # Write totals
  #     for i in ax2.patches:
  #       ax2.text(i.get_x(), i.get_height()*1.02, str(i.get_height()), fontsize=13, color='dimgrey')
  
  return df, fig
###<---------------------------------------------------------- Html title -------------------------------------------------------------->###

st.title('Estadísticas Hospital Materno Neonatal')
st.write("""
Esta página provee una serie de pasos para procesar información a partir de archivos `.csv` específicos del **Hospital Materno Neonatal**.

Se provee, además, una serie de funciones que agilizan el procesamiento y generación de tablas y gráficos a partir de la información procesada.
""")
origin_name = st.selectbox('Seleccione el origen de los datos:', ('Ambulatorio', 'Emergencias', 'Hospitalización'))
if not origin_name:
  st.warning('Por favor, seleccione el origne de los datos')
  st.stop()

if origin_name == 'Ambulatorio':
  # Get filename
  filename = st.text_input('Introduzca la ruta del archivo:')
  if not filename:
    st.warning('Por favor introduzca la ruta del archivo en la celda superior')
    st.stop()
  st.success('Correcto, analizando...')
  # Preprocess .csv
  df = preprocess_ambulatorio(filename)

  year = pd.DatetimeIndex(df['FECHA_HORA_TURNO']).year.unique()[0]
  months = pd.DatetimeIndex(df['FECHA_HORA_TURNO']).month.unique()

  # Title
  st.write(f"""ESTADÍSTICAS {origin_name.upper()}\n
  A continuación se muestra el dataset elegido.\n
  El procesamiento de la base de datos arroja información comprendida en el período mes(es) {months[0]} a {months[-1]} del año {year}.
  """)
  # Complete processed dataframe
  st.dataframe(df)

  # ATENCIONES
  st.write(f'Atenciones por {origin_name}\n')
  servicio=st.checkbox('Por Servicio', value=True)
  seccion=st.checkbox('Por Sección', value=False)
  torta=st.checkbox('Torta', value=False)
  barra=st.checkbox('Barra', value=False)
  atenciones(df, por_servicio=servicio, por_seccion=seccion, torta=torta, barra=barra)

  # MOTIVO ALTA
  st.write('Estadísticas de Motivos de Alta\n')
  st.write('🔑**Nota:** si aparece el valor `nan` significa que los *motivos de alta* NO fueron codificados')
  fig, df_display = motivo_alta(df)
  st.dataframe(df_display)
  st.pyplot(fig)

  # ATENCIONES POR DÍAS DE LA SEMANA
  st.write('Atenciones por Días de la Semana\n')
  servicio=st.checkbox('Por servicio')
  df_at_d_sem, fig= atenciones_por_dia_semana(df, por_servicio=servicio)
#  st.dataframe(df_at_d_sem)
  st.pyplot(fig)

  # ATENCIONES POR DÍAS DE LA SEMANA
  st.write('Atenciones por Días de la Semana\n')
  fig, edades = atenciones_grupo_etareo_ambulatorio(df, por_servicio=False)
  st.dataframe(edades)
  st.pyplot(fig)

  # ATENCIONES POR HORA
  st.write('Atenciones por Hora')
  fig, df_temp = atenciones_por_hora_ambulatorio(df, por_servicio=False)
  st.dataframe(df_temp)
  st.pyplot(fig)

  # Top 20 diagnósticos codificados
  st.write('Top 20 diagnósticos codificados')
  fig, df_temp = top_20_cod_diagnostics_ambulatorio(df, por_servicio=False, por_seccion=False)
  st.dataframe(df_temp)
  st.pyplot(fig)


elif origin_name == 'Emergencias':
  # Get filename
  filename = st.text_input('Introduzca la ruta del archivo:')
  if not filename:
    st.warning('Por favor introduzca la ruta del archivo en la celda superior')
    st.stop()
  st.success('Correcto, analizando...')  

  # Preprocess .csv
  df = preprocess_emergencias(filename) 
  year = pd.DatetimeIndex(df['FECHA_HORA_INGRESO']).year.unique()[0]
  months = pd.DatetimeIndex(df['FECHA_HORA_INGRESO']).month.unique()
  
  st.write(f"""ESTADÍSTICAS {origin_name.upper()}\n
  A continuación se muestra el dataset elegido.\n
  El procesamiento de la base de datos arroja información comprendida en el período mes(es) {months[0]} a {months[-1]} del año {year}.
  """)
  # Complete processed dataframe
  st.dataframe(df)

  # ATENCIONES POR SECCIÓN
  df_temp, fig = atenciones_por_seccion(df)
  st.dataframe(df_temp)
  st.bar_chart(df_temp['CANTIDADES'], use_container_width=True)


  # TOP 20 PROFESIONALES
  df_temp, fig = top_20_professionals(df, por_seccion=False)
  st.dataframe(df_temp)
  st.bar_chart(df_temp[:20])


else:
  st.write('Todavía no llegué acá')
  seccion=st.checkbox('Por sección')
  servicio=st.checkbox('Por servicio')
  torta=st.checkbox('Torta')
  barra=st.checkbox('Barra')
  st.write(seccion, servicio, torta, barra)
  
  genre = st.radio("What's your favorite movie genre", ('Comedy', 'Drama', 'Documentary'))
  if genre == 'Comedy':
    st.write('You selected comedy.')
  else:
    st.write("You didn't select comedy.")
  
  t = st.time_input('Set an alarm for', datetime.time(8, 45))
  st.write('Alarm is set for', t)

  uploaded_file = st.file_uploader("Choose a file")
  if uploaded_file is not None:
    # To read file as bytes:
    bytes_data = uploaded_file.getvalue()
    st.write("filename:", uploaded_file.name)
    #st.write(bytes_data)