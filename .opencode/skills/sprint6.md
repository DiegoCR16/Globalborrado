# Skill: Sprint 6 - Gestión de Caja, Arqueos, Faltantes y Registro de Auditoría

## Objetivos del Sprint
Implementar el control de aperturas/cierres de caja por cajero, desglose físico de billetes, gestión automática de faltantes con descuento salarial y registro completo de auditoría del sistema (RF35, RF46, RF47, RF48, RF49).

## Entidades del Modelo de Datos
- **Caja**: usuario (Cajero), echa_apertura, echa_cierre, estado (ABIERTA, CERRADA, CERRADA_CON_DESCUADRE).
- **BalanceCajaDivisa**: Sostenimiento multimoneda del saldo por caja (saldo_inicial, saldo_actual, saldo_cierre).
- **ArqueoCaja**: caja, 	ipo (APERTURA, PARCIAL, CIERRE), 	otal_calculado, 	otal_real, diferencia, altante, descontar_sueldo (boolean), observaciones.
- **DesgloseBilletes**: Cantidad física de billetes por divisa y denominación.
- **AjusteFaltante**: Registra la justificación y generación de nota de cobro/descuento imputada al cajero notificando a auditoría (RF49).
- **RegistroAuditoria**: Cifrado/JSON con usuario, ccion_realizada, entidad_afectada, datos_anteriores, datos_nuevos, 	imestamp.

## Servicios y Vistas
- GestionCajaService:
  - brir_turno_cajero()
  - procesar_arqueo_y_cierre_caja(): Compara saldos teóricos vs reales. Si hay diferencia, determina si hay faltante y genera AjusteFaltante.
  - calcular_faltante_y_descuento_sueldo()
- CajaViewSet: Interfaz para cajeros.
- AuditoriaService: Middleware/Servicio para auditar operaciones financieras e intentos de acceso fallidos (RF35).
