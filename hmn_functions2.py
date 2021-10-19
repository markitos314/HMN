import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re
import streamlit as st
import datetime

def plot_bar(dataframe, title, x_label, y_label, save_plot, save_path, rotation=90, figsize=(10,7), fontsize=10, dpi=300):
    fig, ax = plt.subplots(figsize=figsize)
    dataframe.plot.bar(fontsize=fontsize,
                        ax=ax,
                        rot=rotation)
    ax.set_title(title)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    for j in ax.patches:
        ax.text(j.get_x(),
                j.get_height()+ax.get_ylim()[1]/100,
                str(j.get_height()),
                fontsize=10,
                color='dimgrey')
    if save_plot:
        fig.savefig(f'{save_path}/{title.replace(" ","_")}_barra.png',
                    dpi=dpi,
                    bbox_inches='tight')
    print(f'Guardando \"{title.replace(" ","_")}_barra.png\" en {save_path}')

    return fig, ax

def plot_pie(dataframe, column, title, y_label, save_plot, save_path, figsize=(10,10), fontsize=10, dpi=300, autopct='%1.2f%%'):
    fig, ax = plt.subplots(figsize=figsize)
    dataframe.plot.pie(y=column,
                    autopct=autopct,
                    labels=None,
                    ax=ax)
    ax.legend(bbox_to_anchor=(1,1),
            loc='upper right',
            labels=dataframe.index)
    ax.set_title(title, fontsize=fontsize)
    ax.set_ylabel(y_label)
    if save_plot:
        fig.savefig(f'{save_path}/{title.replace(" ","_")}_torta.png',
                    dpi=300,
                    bbox_inches='tight')
    print(f'Guardando \"{title.replace(" ","_")}_torta.png\" en {save_path}')
    return fig, ax

def motivo_alta(dataframe):
    df_display = pd.DataFrame(dataframe['MOTIVO_ALTA'].value_counts(dropna=False))
    df_display = df_display.reset_index()
    df_display.columns=['MOTIVO_ALTA', 'CANTIDAD']
    fig, ax = plt.subplots(figsize=(10,10))
    dataframe['MOTIVO_ALTA'].value_counts(dropna=False).plot.barh(ax=ax)
    ax.set_title("Motivo de alta")
    for i in ax.patches:
        if i.get_width() > 1000:
            ax.text(ax.get_xlim()[1]*.8, i.get_y() + 0.20, str(i.get_width()), fontsize=13, color='white')
        else:
            ax.text(i.get_width() + 20, i.get_y() + .20, str(i.get_width()), fontsize=13, color='black')
    return [df_display, fig]
#####################################FUNCIONES EMERGENCIAS#########################################

def preprocess_emergencias(path):
    """
    Function that preprocesses 'emergencias' csv from Pentaho.

    Args:
    path (str): Path to csv to preprocess

    Returns:
    Preprocessed pandas dataframe
    """
    # Read csv
    df = pd.read_csv(path)

    # Get rid of unnecessary columns
    df.drop(columns=[f'Unnamed: {i}' for i in range(18,27,1)], inplace=True)
    df.drop(columns=['Unnamed: 0','Unnamed: 7','Unnamed: 10'], inplace=True)

    # Get rid of unnecessary rows
    df.drop(range(0,6), inplace=True)

    # Set definitive columns
    columns = ['DNI', 'NHC', 'PACIENTE', 'SEXO', 'EDAD', 'FECHA_HORA_INGRESO', 
            'SERVICIO', 'SECCION', 'ALTA_MEDICA', 'MOTIVO_ALTA', 'ALTA_ADMIN', 
            'PROFESIONAL', 'DIAGNOSTICO', 'CIE10', 'DESC_CIE10']
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
    df.sort_values('FECHA_HORA_INGRESO', inplace=True)

    # Convert numerical srt values to int
    df['EDAD'] = df['EDAD'].astype(int)
    #  df['DNI'] = df['DNI'].astype(int)
    #  df['NHC'] = df['NHC'].astype(int)

    # Reset index
    df.reset_index(drop=True, inplace=True)

    # Get dates
    #year = pd.DatetimeIndex(df['FECHA_HORA_INGRESO']).year.unique()[0]
    #months = pd.DatetimeIndex(df['FECHA_HORA_INGRESO']).month.unique()   
    return df

def atenciones_por_seccion(dataframe, save_path, save_plot=False):
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
    print(f"Atenciones por sección (Total = {seccion['CANTIDADES'].sum()})\n")
    #display(seccion)
    print('\n\n')

    # Plot pie
    save_path=save_path
    save_plot=save_plot
    pie = plot_pie(seccion,
                    'CANTIDADES',
                    f'Atenciones por seccion',
                    'CANTIDADES',
                    save_plot=save_plot,
                    save_path=save_path)
        
    # Plot bar
    bar = plot_bar(seccion.drop(columns='% TOTAL'),
                    f'Atenciones por seccion',
                    'SECCIONES',
                    'ATENCIONES',
                    save_plot=save_plot,
                    save_path=save_path)
    return seccion, bar, pie

def top_20_professionals(dataframe, save_path, por_seccion=False, save_plot=False, show_plot=False):

    # Prepare df
    df = pd.DataFrame(dataframe['PROFESIONAL'].value_counts(dropna=False)[:20])
    df['% TOTAL'] = dataframe['PROFESIONAL'].value_counts(dropna=False, normalize=True) *100
    df.columns=['ATENCIONES','% TOTAL']
    print(f'Top 20 profesionales con mayoeres atenciones en todos los servicios')
    #display (df)
    #print('\n')

    save_plot=save_plot
    save_path=save_path  
    # Plot bar
    fig, ax = plot_bar(df.drop(columns='% TOTAL'),
                    f'Top 20 profesionales con mayores atenciones en todos los servicios EMERGENCIAS',
                    'PROFESIONALES',
                    'ATENCIONES',
                    save_plot=save_plot,
                    save_path=save_path)

    if por_seccion:
        secciones = dataframe['SECCION'].unique()
        figures=[]
        professionals=[]
        # Dataframe loop
        for i, secc in enumerate(secciones):
            secc_temp = pd.DataFrame(dataframe[dataframe['SECCION']==secciones[i]])
            professional = pd.DataFrame(secc_temp['PROFESIONAL'].value_counts(dropna=False))[:20]
            professional['% TOTAL'] = secc_temp['PROFESIONAL'].value_counts(dropna=False, normalize=True)*100
            professional.columns=['ATENCIONES', '% TOTAL']      
            # Plot bar
            fig2, axs = plot_bar(professional.drop(columns='% TOTAL'),
                            f'Top 20 profesionales con mayores atenciones en {secc} EMERGENCIAS',
                            'PROFESIONALES',
                            'ATENCIONES',
                            save_plot=save_plot,
                            save_path=save_path)
            figures.append(fig2)
            professionals.append(professional)
        if show_plot==0:
            plt.close(fig2)
    return [df, fig, professionals, figures, show_plot]

def atenciones_por_hora(dataframe, save_path, por_servicio=False, save_plot=False, show_plot=False):
    df_horas = dataframe.FECHA_HORA_INGRESO.dt.hour.value_counts()
    df_horas = df_horas.sort_index()
    year = pd.DatetimeIndex(dataframe['FECHA_HORA_INGRESO']).year.unique()[0]
    months = pd.DatetimeIndex(dataframe['FECHA_HORA_INGRESO']).month.unique()

    # Plot total
    save_plot=save_plot
    save_path=save_path
    fig, ax = plot_bar(df_horas,
                    f'Atenciones según la hora EMERGENCIAS en mes(es) {months[0]} a {months[-1]} de {year}',
                    'HORAS',
                    'ATENCIONES',
                    save_plot=save_plot,
                    save_path=save_path,
                    rotation=0)

    if por_servicio:
        secciones = dataframe['SECCION'].unique()
        dfs = []
        figures = []
        # Loop plot by seccion
        for i, secc in enumerate(secciones):
            secc_temp = pd.DataFrame(dataframe[dataframe['SECCION']==secciones[i]])
            df_horas_temp = secc_temp.FECHA_HORA_INGRESO.dt.hour.value_counts()
            df_horas_temp = df_horas_temp.sort_index()

            fig2, axs = plot_bar(df_horas_temp,
                            f"Atenciones según la hora en {secc} EMERGENCIAS en mes(es) {months[0]} a {months[-1]} de {year}",
                            'HORAS',
                            'ATENCIONES',
                            save_plot=save_plot,
                            save_path=save_path,
                            rotation=0)
            dfs.append(df_horas_temp)
            figures.append(fig2)
        if show_plot==0:
            plt.close(fig2)
    return [df_horas, fig, dfs, figures, show_plot]

def atenciones_por_dia_semana(dataframe, save_path, save_plot=False, show_plot=False, por_seccion=False):
    # Df prepare
    df_dias = dataframe['FECHA_HORA_INGRESO'].dt.dayofweek.value_counts()
    df_dias.sort_index(inplace=True)
    df_dias = df_dias.rename({0:'Lunes', 1:'Martes', 2:'Miércoles', 3:'Jueves', 4:'Viernes', 5:'Sábado', 6:'Domingo'})
    year = pd.DatetimeIndex(dataframe['FECHA_HORA_INGRESO']).year.unique()[0]
    months = pd.DatetimeIndex(dataframe['FECHA_HORA_INGRESO']).month.unique()   

    # Plot
    save_plot=save_plot
    save_path=save_path
    fig, ax=plot_bar(dataframe=df_dias,
                    title=f'Atenciones por día de la semana en mes(es) {months[0]} a {months[-1]} de {year}',
                    x_label='DÍAS',
                    y_label='ATENCIONES',
                    save_plot=save_plot,
                    save_path=save_path,
                    rotation=0)
    #plt.show(fig)  

    if por_seccion:
        # Df by seccion
        secciones = dataframe['SECCION'].unique()
        df_dias_seccion=[]
        figures=[]
        for i, secc in enumerate(secciones):
            secc_temp = pd.DataFrame(dataframe[dataframe['SECCION']==secciones[i]])
            df_dias = secc_temp['FECHA_HORA_INGRESO'].dt.dayofweek.value_counts()
            df_dias.sort_index(inplace=True)
            df_dias = df_dias.rename({0:'Lunes', 1:'Martes', 2:'Miércoles', 3:'Jueves', 4:'Viernes', 5:'Sábado', 6:'Domingo'})

        # Plot
            fig2, axes=plot_bar(df_dias,
                                f'Atenciones en {secc} por día de la semana en mes(es) {months[0]} a {months[-1]} de {year}',
                                'DÍAS',
                                'ATENCIONES',
                                save_plot=save_plot,
                                save_path=save_path,
                                rotation=0)
            df_dias_seccion.append(df_dias)
            figures.append(fig2)
        if show_plot==0:
            plt.close(fig2)
        return [df_dias, fig, df_dias_seccion, figures]
    return [df_dias, fig]

def atenciones_grupo_etareo(dataframe, save_path, show_plot=False, save_plot=False, por_seccion=False):
    # Get months and year of dataframe
    year = pd.DatetimeIndex(dataframe['FECHA_HORA_INGRESO']).year.unique()[0]
    months = pd.DatetimeIndex(dataframe['FECHA_HORA_INGRESO']).month.unique()

    labels=['0 años', '1 a 13', '14 a 21', '22 a 40', '41 a 60', '+61']

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
    save_plot=save_plot
    save_path=save_path
    # Create series to plot pie
    s = pd.Series(grupos, index=labels, name='CANTIDADES')
    # Plot  
    save_plot=save_plot
    save_path=save_path
    fig, ax = plot_pie(dataframe=s,
                        column='CANTIDADES',
                        title=f"Atenciones según grupo etáreo EMERGENCIAS mes(es) {months[0]} a {months[-1]} de {year}",
                        y_label='',
                        save_plot=save_plot,
                        save_path=save_path)

    if por_seccion:
        # By seccion
        secciones = dataframe['SECCION'].unique()
        dfs=[]
        figures=[]
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

            s_temp = pd.Series(grupos, index=labels, name='CANTIDADES')
            # Plot  
            save_plot=save_plot
            save_path=save_path
            fig2, axs = plot_pie(dataframe=s,
                        column='CANTIDADES',
                        title=f"Atenciones según grupo etáreo {secc.upper()} mes(es) {months[0]} a {months[-1]} de {year}",
                        y_label='',
                        save_plot=save_plot,
                        save_path=save_path)
            dfs.append(s_temp)
            figures.append(fig2)
        if show_plot==0:
            plt.close(fig)
        return [s, fig, dfs, figures]
    return [s, fig]

def top_20_cod_diagnostics(dataframe, save_path, save_plot=False, show_plot=False, por_seccion=False):
    # Df prep
    sin_cod = dataframe['CIE10'].isna().sum()
    total_atenciones = len(dataframe.CIE10)
    save_plot=save_plot
    save_path=save_path
    # Plot
    fig, ax=plot_bar(dataframe=dataframe['CIE10'].value_counts()[:20],
                    title='Top 20 diagnósticos codificados con CIE10',
                    x_label='DIAGNÓSTICOS',
                    y_label='CANTIDAD',
                    save_plot=save_plot,
                    save_path=save_path)
    
    if por_seccion:
        # By seccion
        figures=[]
        sin_cod_seccion=[]
        total_atenciones_seccion=[]
        secciones = dataframe['SECCION'].unique()
        for i, secc in enumerate(secciones):
            secc_temp = pd.DataFrame(dataframe[dataframe['SECCION']==secciones[i]])
            sin_cod_temp = secc_temp['CIE10'].isna().sum()
            total_atenciones_temp = len(secc_temp.CIE10)
            if len(secc_temp['CIE10'].value_counts(dropna=False)) > 1:
                fig2, axs = plot_bar(dataframe=secc_temp['CIE10'].value_counts()[:20],
                                    title=f'Top 20 diagnósticos codificados con CIE10 en {secc}',
                                    x_label='DIAGNÓSTICOS',
                                    y_label='CANTIDAD',
                                    save_plot=save_plot,
                                    save_path=save_path)
                if show_plot==0:
                    plt.close(fig2)     
            else:
                fig2, axs = plot_bar(dataframe=secc_temp['CIE10'].value_counts(dropna=False),
                                    title=f'Top 20 diagnósticos codificados con CIE10 en {secc}',
                                    x_label='DIAGNÓSTICOS',
                                    y_label='CANTIDAD',
                                    save_plot=save_plot,
                                    save_path=save_path)            
                if show_plot==0:
                    plt.close(fig2)  
            figures.append(fig2)
            sin_cod_seccion.append(sin_cod_temp)
            total_atenciones_seccion.append(total_atenciones_temp)
        return [fig, sin_cod, total_atenciones, figures, sin_cod_seccion, total_atenciones_seccion]
    return [fig, sin_cod, total_atenciones]

def promedios_tiempo(dataframe):
    st.write('Medias de tiempo según estado del paciente:')
    st.write(f"="*85)
    st.write(f"Entre Ingreso y Alta Médica: {dataframe['DIF_ALTA_MEDICA_INGRESO'].mean()}")
    st.write(f"Entre Alta Médica y Alta Administrativa: {dataframe['DIF_ALTA_ADMIN_MEDICA'].mean()}")
    st.write(f"Entre Ingreso y Alta Administrativa: {dataframe['ESTADIA_TOTAL'].mean()}")
    st.write(f"="*85)
    #st.write(f"Mediana de tiempo entre Alta Médica e Ingreso: {dataframe['DIF_ALTA_MEDICA_INGRESO'].median()}")
    #st.write(f"Mediana de tiempo entre Alta administrativa e Ingreso: {dataframe['ESTADIA_TOTAL'].median()}")
    #st.write(f"Mediana de tiempo entre Alta administrativa y Alta médica: {dataframe['DIF_ALTA_ADMIN_MEDICA'].median()}")

    secciones = dataframe['SECCION'].unique()
    st.subheader('Por Sección')
    for i, secc in enumerate(secciones):
        secc_temp = pd.DataFrame(dataframe[dataframe['SECCION']==secciones[i]])

        st.write(f'\nMedias de tiempo según estado del paciente en **{secc}**:')
        st.write(f"Entre Ingreso y Alta Médica en {secc}: {secc_temp['DIF_ALTA_MEDICA_INGRESO'].mean()}")
        st.write(f"Entre Alta Médica y Alta Administrativa en {secc}: {secc_temp['DIF_ALTA_ADMIN_MEDICA'].mean()}")
        st.write(f"Entre Ingreso y Alta Administrativa en {secc}: {secc_temp['ESTADIA_TOTAL'].mean()}")
        st.write(f"="*85)
        #st.write(f"Mediana de tiempo entre Alta Médica e Ingreso en {secc}: {secc_temp['DIF_ALTA_MEDICA_INGRESO'].median()}")
        #st.write(f"Mediana de tiempo entre Alta administrativa e Ingreso en {secc}: {secc_temp['ESTADIA_TOTAL'].median()}")
        #st.write(f"Mediana de tiempo entre Alta administrativa y Alta médica en {secc}: {secc_temp['DIF_ALTA_ADMIN_MEDICA'].median()}")

#####################################FUNCIONES AMBULATORIOS#########################################

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
    #df['DNI'] = df['DNI'].astype(int)
    #df['NHC'] = df['NHC'].astype(int)

    # Reset index
    df.reset_index(drop=True, inplace=True)
    return df

def atenciones(dataframe, save_path, show_plot=False, save_plot=False, por_servicio=True, por_seccion=False, torta=False, barra=True):
    """
    Function that generates statistics from emergency dataframe

    Args:
        dataframe: pandas dataframe

    Returns:

    """
    year = pd.DatetimeIndex(dataframe['FECHA_HORA_TURNO']).year.unique()[0]
    months = pd.DatetimeIndex(dataframe['FECHA_HORA_TURNO']).month.unique() 

    ### Atenciones por sección
    save_path=save_path
    save_plot=save_plot

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

        if torta:
            # Plot pie
            df_bar = df.set_index('SERVICIO') #change index for plotting SERVICIOS not numbers
            fig, ax = plot_pie(dataframe=df_bar, 
                               column=f'CANTIDADES',
                               title=f'Atenciones por servicio AMBULATORIO mes(es) {months[0]} a {months[-1]} de {year}',
                               y_label='ATENCIONES',
                               save_plot=save_plot,
                               save_path=save_path)
            if show_plot ==0:
                plt.close(fig)

        if barra:
            # Plot bar
            df_bar = df.drop(columns='% TOTAL')
            df_bar = df_bar.set_index('SERVICIO') #change index for plotting SERVICIOS not numbers
            fig2, ax2 = plot_bar(dataframe=df_bar,
                                title=f'Atenciones por servicio AMBULATORIO mes(es) {months[0]} a {months[-1]} de {year}',
                                x_label='SERVICIOS',
                                y_label='ATENCIONES',
                                save_plot=save_plot,
                                save_path=save_path)
            if show_plot ==0:
                plt.close(fig2)    

    if por_seccion:
        # Get all servicios
        servicios = dataframe['SERVICIO'].unique()
        dfs=[]
        figures_torta=[]
        figures_barra=[]
        for i, secc in enumerate(servicios):
            # Create dataframe with only servicios[i]
            df_temp = pd.DataFrame(dataframe[dataframe['SERVICIO']==servicios[i]])
            # Create dataframe with value counts of servicios[i]
            df_temp = pd.DataFrame(df_temp['SECCION'].value_counts(dropna=False))
            # Reset indexes
            df_temp = df_temp.reset_index()
            # Set columns names
            df_temp.columns=['SECCION','CANTIDADES']
            print(f"Atenciones en {servicios[i]} (Total = {df['CANTIDADES'].sum()})\n")
            dfs.append(df_temp)
            if torta:
                # Plot pie
                df_bar = df_temp.set_index('SECCION') #change index for plotting SERVICIOS not numbers
                fig_torta, ax = plot_pie(dataframe=df_bar,
                                        column='CANTIDADES',
                                        title=f'Atenciones en {servicios[i]} AMBULATORIO mes(es) {months[0]} a {months[-1]} de {year}',
                                        y_label='ATENCIONES',
                                        save_plot=save_plot,
                                        save_path=save_path)
                if show_plot ==0:
                    plt.close(fig_torta)
            figures_torta.append(fig_torta)
            if barra:
                # Plot bar
                fig_barra, ax = plot_bar(dataframe=df_temp.set_index('SECCION'),
                                        title=f'Atenciones en {servicios[i]} AMBULATORIO mes(es) {months[0]} a {months[-1]} de {year}',
                                        x_label='SECCIONES',
                                        y_label='ATENCIONES',
                                        save_plot=save_plot,
                                        save_path=save_path)
                if show_plot ==0:
                    plt.close(fig_barra)
            figures_barra.append(fig_barra)
    return [df, fig, fig2, dfs, figures_torta, figures_barra]
    ##################### ver los return dentro de los if####################################

def top_20_cod_diagnostics_ambulatorio(dataframe, save_path, save_plot=False, show_plot=False, por_servicio=False, por_seccion=False):
    # Get year and months from dataframe
    year = pd.DatetimeIndex(dataframe['FECHA_HORA_TURNO']).year.unique()[0]
    months = pd.DatetimeIndex(dataframe['FECHA_HORA_TURNO']).month.unique()

    sin_cod = dataframe['CIE10'].isna().sum()
    total_atenciones = len(dataframe.CIE10)

    save_plot=save_plot
    save_path=save_path
    # Plot bar
    fig, ax = plot_bar(dataframe=dataframe['CIE10'].value_counts()[:20],
                        title=f'Top 20 diagnósticos codificados con CIE10 AMBULATORIO en mes(es) {months[0]} a {months[-1]} de {year}',
                        x_label='CÓDIGO CIE10',
                        y_label='CANTIDAD',
                        save_plot=save_plot,
                        save_path=save_path,
                        rotation=0)
    
    if por_seccion:
        # By seccion
        figures_secc=[]
        sin_cod_secc=[]
        total_secc=[]
        secciones = dataframe['SECCION'].unique()
        for i, secc in enumerate(secciones):
            secc_temp = pd.DataFrame(dataframe[dataframe['SECCION']==secciones[i]])
            sin_cod_temp = secc_temp['CIE10'].isna().sum()
            total_atenciones_temp = len(secc_temp.CIE10)
            # If - else, in case seccion only has nan values
            if len(secc_temp['CIE10'].value_counts(dropna=False)) > 1:      
            # Plot bar
                fig_secc, axs = plot_bar(dataframe=secc_temp['CIE10'].value_counts()[:20],
                                    title=f'Top 20 diagnósticos codificados con CIE10 AMBULATORIO en {secc} en mes(es) {months[0]} a {months[-1]} de {year}',
                                    x_label='CÓDIGO CIE10',
                                    y_label='CANTIDAD',
                                    save_plot=save_plot,
                                    save_path=save_path,
                                    rotation=0)
                if show_plot==0:
                    plt.close(fig_secc)
                figures_secc.append(fig_secc)
                sin_cod_secc.append(sin_cod_temp)
                total_secc.append(total_atenciones_temp)
            else:
                fig_secc, axs = plot_bar(dataframe=secc_temp['CIE10'].value_counts(dropna=False),
                                    title=f'Top 20 diagnósticos codificados con CIE10 AMBULATORIO en {secc} en mes(es) {months[0]} a {months[-1]} de {year}',
                                    x_label='CÓDIGO CIE10',
                                    y_label='CANTIDAD',
                                    save_plot=save_plot,
                                    save_path=save_path,
                                    rotation=0)        
                if show_plot==0:
                    plt.close(fig_secc)
                figures_secc.append(fig_secc)
                sin_cod_secc.append(sin_cod_temp)
                total_secc.append(total_atenciones_temp)                
    if por_servicio:  
        # By service
        servicios = dataframe['SERVICIO'].unique()
        figures_serv=[]
        sin_cod_serv=[]
        total_serv=[]
        for i, serv in enumerate(servicios):
            serv_temp = pd.DataFrame(dataframe[dataframe['SERVICIO']==servicios[i]])
            sin_cod_temp = serv_temp['CIE10'].isna().sum()
            total_atenciones_temp = len(serv_temp.CIE10)

            if len(serv_temp['CIE10'].value_counts(dropna=False)) > 1:
                fig_serv, axs = plot_bar(dataframe=serv_temp['CIE10'].value_counts()[:20],
                                        title=f'Top 20 diagnósticos codificados con CIE10 AMBULATORIO en {serv} en mes(es) {months[0]} a {months[-1]} de {year}',
                                        x_label='CÓDIGO CIE10',
                                        y_label='CANTIDAD',
                                        save_plot=save_plot,
                                        save_path=save_path,
                                        rotation=0)        
                if show_plot==0:
                    plt.close(fig_serv)
                figures_serv.append(fig_serv)
                sin_cod_serv.append(sin_cod_temp)
                total_serv.append(total_atenciones_temp)
            else:
                fig_serv, axs = plot_bar(dataframe=serv_temp['CIE10'].value_counts(dropna=False),
                                        title=f'Top 20 diagnósticos codificados con CIE10 AMBULATORIO en {serv} en mes(es) {months[0]} a {months[-1]} de {year}',
                                        x_label='CÓDIGO CIE10',
                                        y_label='CANTIDAD',
                                        save_plot=save_plot,
                                        save_path=save_path,
                                        rotation=0)
                figures_serv.append(fig_serv)
                sin_cod_serv.append(sin_cod_temp)
                total_serv.append(total_atenciones_temp)                
                if show_plot==0:
                    plt.close(fig_serv)
    return [fig, sin_cod, total_atenciones, figures_secc, sin_cod_secc, total_secc, figures_serv, sin_cod_serv, total_serv]

def atenciones_por_hora_ambulatorio(dataframe, save_path, show_plot=False, save_plot=False, por_servicio=False):
    # Get year and months from dataframe
    year = pd.DatetimeIndex(dataframe['FECHA_HORA_TURNO']).year.unique()[0]
    months = pd.DatetimeIndex(dataframe['FECHA_HORA_TURNO']).month.unique()

    df_horas = dataframe.FECHA_HORA_TURNO.dt.hour.value_counts()
    df_horas = df_horas.sort_index()

    # Plot total
    save_path=save_path
    save_plot=save_plot
    fig, ax = plot_bar(dataframe=df_horas,
                        title=f'Atenciones totales por hora AMBULATORIO en mes(es) {months[0]} a {months[-1]} de {year}',
                        x_label='HORAS',
                        y_label='ATENCIONES',
                        save_plot=save_plot,
                        save_path=save_path,
                        rotation=0)

    if por_servicio:
        servicios = dataframe['SERVICIO'].unique()
        dfs=[]
        figures=[]
        # Loop plot by seccion
        for i, serv in enumerate(servicios):
            serv_temp = pd.DataFrame(dataframe[dataframe['SERVICIO']==servicios[i]])
            df_horas_temp = serv_temp.FECHA_HORA_TURNO.dt.hour.value_counts()
            df_horas_temp = df_horas_temp.sort_index()
            dfs.append(df_horas_temp)
            # Plot
            fig_serv, axs = plot_bar(dataframe=df_horas_temp,
                                title=f'Atenciones por hora {serv} AMBULATORIO mes(es) {months[0]} a {months[-1]} de {year}',
                                x_label='HORAS',
                                y_label='ATENCIONES',
                                save_plot=save_plot,
                                save_path=save_path,
                                rotation=0)
            figures.append(fig_serv)
            if show_plot==0:
                plt.close(fig_serv)
        return [df_horas, fig, dfs, figures]
    return [df_horas, fig]

def atenciones_por_dia_semana_ambulatorio(dataframe, save_path, show_plot=False, save_plot=False, por_servicio=False):
    # Get months and year of dataframe
    year = pd.DatetimeIndex(dataframe['FECHA_HORA_TURNO']).year.unique()[0]
    months = pd.DatetimeIndex(dataframe['FECHA_HORA_TURNO']).month.unique()

    # Df prepare
    df_dias = dataframe['FECHA_HORA_TURNO'].dt.dayofweek.value_counts()
    df_dias.sort_index(inplace=True)
    df_dias = df_dias.rename({0:'Lunes', 1:'Martes', 2:'Miércoles', 3:'Jueves', 4:'Viernes', 5:'Sábado', 6:'Domingo'})

    # Plot bar
    save_plot=save_plot
    save_path=save_path
    fig, ax = plot_bar(dataframe=df_dias,
                        title=f"Atenciones en todos los servicios por día de la semana AMBULATORIO en mes(es) {months[0]} a {months[-1]} de {year}",
                        x_label='DÍAS DE LA SEMANA',
                        y_label='ATENCIONES',
                        save_plot=save_plot,
                        save_path=save_path,
                        rotation=0)

    # Df by seccion
    if por_servicio:
        servicios = dataframe['SERVICIO'].unique()
        figures=[]
        for i, serv in enumerate(servicios):
            serv_temp = pd.DataFrame(dataframe[dataframe['SERVICIO']==servicios[i]])
            df_dias = serv_temp['FECHA_HORA_TURNO'].dt.dayofweek.value_counts()
            df_dias.sort_index(inplace=True)
            df_dias = df_dias.rename({0:'Lunes', 1:'Martes', 2:'Miércoles', 3:'Jueves', 4:'Viernes', 5:'Sábado', 6:'Domingo'})
            # Plot bar
            fig_serv, axs = plot_bar(dataframe=df_dias,
                                    title=f"Atenciones en {serv} por día de la semana AMBULATORIO en mes(es) {months[0]} a {months[-1]} de {year}",
                                    x_label='DÍAS DE LA SEMANA',
                                    y_label='ATENCIONES',
                                    save_plot=save_plot,
                                    save_path=save_path,
                                    rotation=0)
            figures.append(fig_serv)
            if show_plot==0:
                plt.close(fig_serv)
        return [df_dias, fig, figures]
    return [df_dias, fig]

def atenciones_grupo_etareo_ambulatorio(dataframe, save_path, show_plot=False, save_plot=False, por_servicio=False):
    # Get months and year of dataframe
    year = pd.DatetimeIndex(dataframe['FECHA_HORA_TURNO']).year.unique()[0]
    months = pd.DatetimeIndex(dataframe['FECHA_HORA_TURNO']).month.unique()

    labels=['0 años', '1 a 13', '14 a 21', '22 a 40', '41 a 60', '+61']

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

    # Create series to plot pie
    s = pd.Series(grupos, index=labels, name='EDADES')
    # Plot  
    save_plot=save_plot
    save_path=save_path
    fig, ax = plot_pie(dataframe=s,
                        column='EDADES',
                        title=f"Atenciones según grupo etáreo AMBULATORIO mes(es) {months[0]} a {months[-1]} de {year}",
                        y_label='',
                        save_plot=save_plot,
                        save_path=save_path)

    if por_servicio:
    # By seccion
        servicios = dataframe['SERVICIO'].unique()
        dfs = []
        figures = []
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

            s_temp = pd.Series(grupos, index=labels, name='EDADES')
            dfs.append(s_temp)
            # Plot  
            save_plot=save_plot
            save_path=save_path
            fig_secc, axs = plot_pie(dataframe=s_temp,
                        column='EDADES',
                        title=f"Atenciones según grupo etáreo {serv.upper()} AMBULATORIO mes(es) {months[0]} a {months[-1]} de {year}",
                        y_label='',
                        save_plot=save_plot,
                        save_path=save_path)
            figures.append(fig_secc)
            if show_plot==0:
                plt.close(fig_secc)
        return [s, fig, dfs, figures]
    return [s, fig]

###################################FUNCIONES HOSPITALIZACION######################################

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
  #df['DNI'] = df['DNI'].astype(int)
  #df['NHC'] = df['NHC'].astype(int)

  # Reset index
  df.reset_index(drop=True, inplace=True)
  return df

def atenciones_hosp(dataframe, save_path, show_plot=False, save_plot=False):
    year = pd.DatetimeIndex(dataframe['FECHA_HORA_INGRESO']).year.unique()[0]
    months = pd.DatetimeIndex(dataframe['FECHA_HORA_INGRESO']).month.unique()    
    # Defino los dos servicios principales
    toco = dataframe[dataframe['SERVICIO']=='Tocoginecología']
    neo = dataframe[dataframe['SERVICIO']=='Neonatología']
    # Genero df's con totales
    toco_df = pd.DataFrame({'ATENCIONES':toco['SECCION'].value_counts(),
                            '% TOTAL':np.round(toco['SECCION'].value_counts(normalize=True)*100,2)})
    neo_df = pd.DataFrame({'ATENCIONES':neo['SECCION'].value_counts(),
                            '% TOTAL':np.round(neo['SECCION'].value_counts(normalize=True)*100,2)})
    total_toco = toco_df.ATENCIONES.sum()
    total_neo = neo_df.ATENCIONES.sum()

    save_plot=save_plot
    save_path=save_path

    # Plot
    fig1, ax1 = plot_bar(dataframe=toco_df.ATENCIONES,
                        title=f'Atenciones en Tocoginecología HOSPITALIZACIÓN Mes(es) {months[0]} a {months[-1]} de {year}',
                        x_label='SECCION',
                        y_label='ATENCIONES POR SECCIÓN',
                        save_plot=save_plot,
                        save_path=save_path,
                        rotation=45)
    
    if show_plot==0:
        plt.close(fig1)
    
    fig2, ax2 = plot_bar(dataframe=neo_df.ATENCIONES,
                        title=f'Atenciones en Neonatología HOSPITALIZACIÓN Mes(es) {months[0]} a {months[-1]} de {year}',
                        x_label='SECCION',
                        y_label='ATENCIONES POR SECCIÓN',
                        save_plot=save_plot,
                        save_path=save_path,
                        rotation=45)  

    if show_plot==0:
        plt.close(fig2)
    
    fig3, ax3 = plot_pie(dataframe=toco_df,
                        column='ATENCIONES',
                        title=f'Atenciones en Tocoginecología HOSPITALIZACIÓN Mes(es) {months[0]} a {months[-1]} de {year}',
                        y_label='ATENCIONES POR SECCIÓN',
                        save_plot=save_plot,
                        save_path=save_path)

    if show_plot==0:
        plt.close(fig3)
    
    fig4, ax4 = plot_pie(dataframe=neo_df,
                        column='ATENCIONES',
                        title=f'Atenciones en Neonatología HOSPITALIZACIÓN Mes(es) {months[0]} a {months[-1]} de {year}',
                        y_label='ATENCIONES POR SECCIÓN',
                        save_plot=save_plot,
                        save_path=save_path)
    if show_plot==0:
        plt.close(fig4)
    return [toco_df, neo_df, fig1, fig2, fig3, fig4, total_toco, total_neo]

def top_20_professionals_hosp(dataframe, save_path, show_plot=False, save_plot=False):
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

    save_plot=save_plot
    save_path=save_path
    # Graficamos con totales
    fig_toco, ax = plot_bar(dataframe=toco_df.ATENCIONES[:20],
                            title=f'Top 20 profesionales con más atenciones en Tocoginecología HOSPITALIZACIÓN',
                            x_label='PROFESIONALES',
                            y_label='ATENCIONES',
                            save_plot=save_plot,
                            save_path=save_path)
    if show_plot==0:
        plt.close(fig_toco)

    fig_neo, ax2 = plot_bar(dataframe=neo_df.ATENCIONES[:20],
                            title=f'Top 20 profesionales con más atenciones en Neonatología HOSPITALIZACIÓN',
                            x_label='PROFESIONALES',
                            y_label='ATENCIONES',
                            save_plot=save_plot,
                            save_path=save_path)
    if show_plot==0:
        plt.close(fig_neo)
    return [toco_df, neo_df, fig_toco, fig_neo]

def atenciones_por_hora_hosp(dataframe, save_path, show_plot=False, save_plot=False, por_servicio=False):
    # Get year and months from dataframe
    year = dataframe.FECHA_HORA_INGRESO.dt.year.unique()[0]
    months = dataframe.FECHA_HORA_INGRESO.dt.month.unique()

    df_horas = pd.DataFrame({'ATENCIONES':dataframe.FECHA_HORA_INGRESO.dt.hour.value_counts()})
    df_horas = df_horas.sort_index()
    #print('Atenciones por hora | HOSPITALIZACIÓN')
    #display(df_horas)
    
    save_plot=save_plot
    save_path=save_path
    # Plot  
    fig, ax = plot_bar(dataframe=df_horas,
                    title=f'Atenciones por hora HOSPITALIZACIÓN mes(es) {months[0]} a {months[-1]} de {year}',
                    x_label='HORAS',
                    y_label='ATENCIONES',
                    save_plot=save_plot,
                    save_path=save_path,
                    rotation=0)
    
    if por_servicio:
        secciones = dataframe['SECCION'].unique()
        figures=[]
        # Loop plot by seccion
        for i, secc in enumerate(secciones):
            secc_temp = pd.DataFrame(dataframe[dataframe['SECCION']==secciones[i]])
            df_horas_temp = secc_temp.FECHA_HORA_INGRESO.dt.hour.value_counts()
            df_horas_temp = df_horas_temp.sort_index()
            
            fig_secc, axs = plot_bar(dataframe=df_horas,
                                    title=f'Atenciones por hora {secc} HOSPITALIZACIÓN mes(es) {months[0]} a {months[-1]} de {year}',
                                    x_label='HORAS',
                                    y_label='ATENCIONES',
                                    save_plot=save_plot,
                                    save_path=save_path,
                                    rotation=0)
            figures.append(fig_secc)
            if show_plot==0:
                plt.close(fig_secc)
        return [fig, figures]
    return fig