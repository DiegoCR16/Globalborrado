# Skill: Sprint 5 - Integraciones con Pasarelas de Pago, SIPAP, Billeteras y SIFEN

## Objetivos del Sprint
Implementar las integraciones externas mockeadas/pseudo-integraciones para cobros, retiros y facturación electrónica oficial según el ERS (RF29, RF30, RF31, RF41, RF42, RF44, RNF17, RNF18).

## Módulos e Integraciones
1. **Pasarela de Pagos / Billeteras / SIPAP (RF29, RF41, RF42, RF44, RNF17)**:
   - MetodoPago: Tarjeta (Débito/Crédito via Bancard), Transferencia (SIPAP/Bancos), Billetera (Tigo Money, Western Union, EuroTransfer), Retiro en caja (Pickup).
   - DetalleMetodoPago: Almacena token de tarjeta, número de cuenta/CVC cifrados (AES-256), número celular, etc.
   - PasarelaPagosAPIService: Pseudo-integración con métodos procesar_pago_virtual() y confirmar_recepcion_fondos().
2. **Facturación Electrónica SIFEN (RF30, RF31, RNF18)**:
   - Factura: 
umero_factura, pago (OneToOne), estado (EMITIDA, APROBADA, RECHAZADA), fecha_emision, 
espuesta_api_fiscal (JSON).
   - FacturacionAPIService:
     - emitir_comprobante_fiscal(transaccion_id): Envía datos a SIFEN y recibe CDC/QR.
     - sincronizar_estado_factura().
   - Envío automático de factura en PDF al correo del cliente.
