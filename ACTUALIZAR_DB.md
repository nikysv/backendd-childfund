# 🔄 Actualizar Base de Datos

## Agregar tabla de Transacciones (Finance)

Ejecuta este comando para crear la nueva tabla `transactions`:

```powershell
python setup_db.py
```

Esto creará:
- ✅ Tabla `transactions` para ingresos y egresos
- ✅ Mantiene todas las tablas existentes de aprendizaje

## Verificar

Prueba el endpoint de salud:

```powershell
curl http://localhost:5000/api/finance/health
```

Deberías ver:
```json
{
  "success": true,
  "message": "Finance API is running",
  "transactions_count": 0
}
```

## Endpoints Disponibles

### Transacciones
- `GET /api/finance/transactions?user_id=xxx` - Listar transacciones
- `POST /api/finance/transactions` - Crear transacción
- `GET /api/finance/transactions/:id` - Ver transacción
- `PUT /api/finance/transactions/:id` - Actualizar transacción
- `DELETE /api/finance/transactions/:id` - Eliminar transacción
- `GET /api/finance/summary/:user_id` - Resumen financiero

