# Skill: Sprint 3 - Motor Cambiario, Cotizaciones y Simulación

## Objetivos del Sprint
Implementar la lógica central del tipo de cambio, simulación de conversiones y las reglas de negocio financieras (descuentos por categoría de cliente, márgenes de ganancia y límites) según el ERS (RF10, RF13, RF14, RF16, RF20, RF21, RF22, RF23, RF33, RF43).

## Entidades del Modelo de Datos
- **Divisa**: codigo_iso (USD, EUR, BRL, ARS, PYG - Moneda base: PYG), 
ombre, simbolo, ctiva.
- **TasaCambio**: divisa (FK), precio_compra, precio_venta, echa_actualizacion.
- **Cliente**: Categorías (MINORISTA, CORPORATIVO, VIP).

## Reglas de Negocio Financieras (CRÍTICO)
1. **Moneda Base**: El Guaraní Paraguayo (PYG) es la moneda base del sistema (RF43).
2. **Descuentos/Beneficios por Categoría de Cliente (RF10)**:
   - **MINORISTA**: Sin beneficios adicionales.
   - **VIP** (Operaciones > 50.000.000 PYG): Beneficio del **2%** en compra de divisas.
   - **CORPORATIVO** (Operaciones > 100.000.000 PYG): Beneficio del **4%** en compra de divisas.
3. **Validación de Límites Transaccionales (RF33)**:
   - Monto mínimo por transacción: equivalente a **50.000 PYG**.
   - Monto máximo por transacción: equivalente a **1.000.000.000 PYG**.
4. **Cálculo de Conversiones**:
   - Compra: Monto_Destino = (Monto_Origen * Tasa_Compra) * (1 - Beneficio_Categoria).
   - Venta: Monto_Destino = (Monto_Origen / Tasa_Venta).

## Servicios y Vistas a Implementar
- TasaCambio: Endpoints para listar tasas actualizadas, histórico de 7 días para gráficos (RF22) y actualización por Analistas Cambiarios (RF16).
- ProcesadorTransaccionesService.simular_compra_venta(): Servicio que calcula el monto exacto a recibir, comisiones y aplicabilidad de beneficios según la categoría del cliente.
- Dashboard / DashboardViewSet: Gráfico de barras de ganancias por moneda de manera mensual (RF20, RF40).
