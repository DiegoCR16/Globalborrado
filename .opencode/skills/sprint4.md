# Skill: Sprint 4 - Procesamiento de Transacciones de Compra/Venta

## Objetivos del Sprint
Implementar el ciclo de vida completo de las operaciones transaccionales cambiarias en web y ventanilla, manejo de estados, historial y reglas de validación de saldos según el ERS (RF19, RF24, RF25, RF26, RF27, RF28, RF33, RF38).

## Entidades y Modelos
- **Transaccion**: 
umero_operacion, cliente (FK), divisa_origen, divisa_destino, monto_origen, monto_destino, 	asa_aplicada, estado_actual (PENDIENTE, PAGADO, CANCELADO, ANULADO), fecha_hora.
- **DetalleTransaccion**: subtotal, comision.
- **HistorialEstadoTransaccion**: estado_anterior, estado_nuevo, motivo_cambio, 	imestamp, modificado_por.

## Flujo Transaccional
1. **Validación Previa (RF19, RF33)**:
   - Verificar que el usuario tenga un Cliente asociado.
   - Verificar saldo suficiente de la divisa solicitada.
   - Respetar los límites [50.000 PYG - 1.000.000.000 PYG].
2. **Creación**: Se genera la transacción en estado PENDIENTE.
3. **Procesamiento**: Al recibir confirmación del pago/caja, cambia a PAGADO.
4. **Cancelación / Anulación**: Cambio de estado auditado registrando el motivo en HistorialEstadoTransaccion.

## Servicios y Vistas
- TransaccionViewSet: Endpoints para crear_transaccion_web(), crear_transaccion_ventanilla(), cambiar_estado_transaccion() y obtener_historial_status().
- ProcesadorTransaccionesService: Control transaccional con @transaction.atomic en la BBDD para prevenir condiciones de carrera en saldos.
