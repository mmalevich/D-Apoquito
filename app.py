import streamlit as st
import numpy as np
import pandas as pd

def calcular_resultado(kg_comprados, adpv, conversion_ms, dias, rendimiento, precio_kg_comprado,
                        costo_kg_dieta, precio_venta):
    # Cálculos intermedios
    consumo_ms_kg = adpv * conversion_ms
    kg_ganados = adpv * dias
    kg_salida = kg_comprados + kg_ganados
    total_usd_compra = kg_comprados * precio_kg_comprado
    costo_alimentacion_total = consumo_ms_kg * dias * costo_kg_dieta
    ingreso_usd = kg_salida * (rendimiento / 100) * precio_venta
    gasto_vta_impuesto = 0.01 * ingreso_usd
    gasto_estructura_estadia = dias * 0.38  # Se toma el gasto estructura/día/animal como fijo
    
    # Resultado final con todos los costos incluidos
    resultado = ingreso_usd - total_usd_compra - costo_alimentacion_total - gasto_estructura_estadia - gasto_vta_impuesto - 2 - 2
    return round(resultado), kg_salida, costo_alimentacion_total, ingreso_usd, total_usd_compra, gasto_vta_impuesto, gasto_estructura_estadia

def calcular_composicion(kg_comprados, kg_salida, costo_alimentacion_total, ingreso_usd, total_usd_compra, gasto_vta_impuesto, gasto_estructura_estadia, rendimiento, precio_kg_comprado, precio_venta, dias, adpv):
    kg_ganados = dias * adpv
    margen_compra_venta = ((precio_venta * (rendimiento / 100)) - precio_kg_comprado) * kg_comprados
    margen_alimentacion = ((precio_venta * (rendimiento / 100)) - ((gasto_estructura_estadia + costo_alimentacion_total) / kg_ganados)) * kg_ganados
    gastos_compra_venta = - (gasto_vta_impuesto + 2 + 2)
    resultado_total = margen_compra_venta + margen_alimentacion + gastos_compra_venta
    
    return {
        "Margen de compra venta": round(margen_compra_venta),
        "Margen de alimentación": round(margen_alimentacion),
        "Gastos de compra venta": round(gastos_compra_venta),
        "Resultado Total": round(resultado_total)
    }

def generar_sensibilidad_precios(kg_comprados, adpv, conversion_ms, dias, rendimiento, costo_kg_dieta, precio_kg_comprado, precio_venta):
    precios_compra = [round(precio_kg_comprado + (i * 0.05), 2) for i in range(-5, 6)]
    precios_venta = [round(precio_venta + (i * 0.05), 2) for i in range(-5, 6)]
    
    data = []
    for pc in precios_compra:
        row = []
        for pv in precios_venta:
            resultado, _, _, _, _, _, _ = calcular_resultado(kg_comprados, adpv, conversion_ms, dias, rendimiento, pc, costo_kg_dieta, pv)
            row.append(resultado)
        data.append(row)
    
    df_sensibilidad = pd.DataFrame(data, index=[f"Compra: {pc}" for pc in precios_compra], 
                                   columns=[f"Venta: {pv}" for pv in precios_venta])
    return df_sensibilidad

def generar_sensibilidad_conversion_adpv(kg_comprados, adpv, conversion_ms, dias, rendimiento, costo_kg_dieta, precio_kg_comprado, precio_venta):
    adpv_values = [round(adpv + (i * 0.2), 2) for i in range(-5, 6)]
    conversion_values = [round(conversion_ms + (i * 0.2), 2) for i in range(-5, 6)]
    
    data = []
    for conv in conversion_values:
        row = []
        for a in adpv_values:
            resultado, _, _, _, _, _, _ = calcular_resultado(kg_comprados, a, conv, dias, rendimiento, precio_kg_comprado, costo_kg_dieta, precio_venta)
            row.append(resultado)
        data.append(row)
    
    df_sensibilidad = pd.DataFrame(data, index=[f"Conv: {conv}" for conv in conversion_values], 
                                   columns=[f"ADPV: {a}" for a in adpv_values])
    return df_sensibilidad

def colorear_celda(val):
    if val < 0:
        color = 'background-color: red; color: white'
    elif 0 <= val <= 50:
        color = 'background-color: yellow; color: black'
    elif 51 <= val <= 89:
        color = 'background-color: lightgreen; color: black'
    else:
        color = 'background-color: green; color: white; font-weight: bold'
    return color

st.title("Simulador de Compra para Feedlot")

# Inputs de usuario
kg_comprados = st.number_input("Kg comprados", value=350)
adpv = st.number_input("ADPV (Aumento Diario de Peso Vivo)", value=1.4)
conversion_ms = st.number_input("Conversión en MS", value=7.3)
dias = st.number_input("Días", value=120)
rendimiento = st.number_input("Rendimiento 4ta balanza (%)", value=57)
precio_kg_comprado = st.number_input("Precio Kg comprado puesto", value=2.2)
costo_kg_dieta = st.number_input("Costo Kg dieta prom MS", value=0.26)
precio_venta = st.number_input("Precio de venta en 4ta balanza", value=4.0)

if st.button("Calcular Resultado"):
    resultado, kg_salida, costo_alimentacion_total, ingreso_usd, total_usd_compra, gasto_vta_impuesto, gasto_estructura_estadia = calcular_resultado(
        kg_comprados, adpv, conversion_ms, dias, rendimiento, precio_kg_comprado, costo_kg_dieta, precio_venta)
    st.success(f"Resultado: USD {resultado}")
    
    # Mostrar composición del resultado
    st.subheader("Composición del Resultado")
    composicion = calcular_composicion(kg_comprados, kg_salida, costo_alimentacion_total, ingreso_usd, total_usd_compra, gasto_vta_impuesto, gasto_estructura_estadia, rendimiento, precio_kg_comprado, precio_venta, dias, adpv)
    df_composicion = pd.DataFrame(composicion.items(), columns=["Concepto", "Valor (USD)"])
    st.dataframe(df_composicion)
    
    # Generar análisis de sensibilidad precios
    st.subheader("Análisis de Sensibilidad: Resultado Total según Precios de Compra y Venta")
    df_sensibilidad_precios = generar_sensibilidad_precios(kg_comprados, adpv, conversion_ms, dias, rendimiento, costo_kg_dieta, precio_kg_comprado, precio_venta)
    df_coloreado_precios = df_sensibilidad_precios.style.map(colorear_celda)
    st.dataframe(df_coloreado_precios)
    
    # Generar análisis de sensibilidad conversión y ADPV
    st.subheader("Análisis de Sensibilidad: Resultado Total según Conversión MS y ADPV")
    df_sensibilidad_conv_adpv = generar_sensibilidad_conversion_adpv(kg_comprados, adpv, conversion_ms, dias, rendimiento, costo_kg_dieta, precio_kg_comprado, precio_venta)
    df_coloreado_conv_adpv = df_sensibilidad_conv_adpv.style.map(colorear_celda)
    st.dataframe(df_coloreado_conv_adpv)
    # =========================
    # KPIs FINALES (SIN MODIFICAR FUNCIONES)
    # =========================

    # Recalculamos acá (simple y seguro)
    kg_ganados = adpv * dias

    if kg_ganados > 0:
        costo_kg_producido = (costo_alimentacion_total + gasto_estructura_estadia) / kg_ganados
    else:
        costo_kg_producido = 0

    precio_kg_producido = precio_venta * (rendimiento / 100)
    margen_kg_producido = precio_kg_producido - costo_kg_producido

    st.markdown("<br><br>", unsafe_allow_html=True)

    # Fila: costo y precio
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            f"""
            <div style='text-align: center;'>
                <div style='font-size:18px; color:gray;'>Costo Kg Producido</div>
                <div style='font-size:36px; font-weight:bold; color:#2E8B57;'>
                    USD {costo_kg_producido:.2f}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            f"""
            <div style='text-align: center;'>
                <div style='font-size:18px; color:gray;'>Precio Kg Producido</div>
                <div style='font-size:36px; font-weight:bold; color:#1f77b4;'>
                    USD {precio_kg_producido:.2f}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Margen grande
    st.markdown("<br>", unsafe_allow_html=True)

    color_margen = "#2E8B57" if margen_kg_producido > 0 else "#d00000"

    st.markdown(
        f"""
        <div style='text-align: center;'>
            <div style='font-size:22px; color:#666;'>MARGEN KG PRODUCIDO</div>
            <div style='font-size:60px; font-weight:bold; color:{color_margen};'>
                USD {margen_kg_producido:.2f}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
