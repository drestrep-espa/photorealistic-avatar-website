# Despliegue AWS

La plantilla crea:

- un bucket privado para el frontend;
- una distribución CloudFront con OAC;
- un bucket privado para proyectos e informes;
- una Lambda para el chatbot;
- una Lambda para generar informes.

El frontend se publica en
`https://normativa-precheck.endrokosai.com`. Todos los recursos de aplicación
se crean en Irlanda (`eu-west-1`). El certificado de CloudFront se crea en
`us-east-1`, que es la región obligatoria de ACM para CloudFront.

Los proyectos bajo `uploads/` caducan al día y los informes bajo `reports/`
caducan a los siete días. Las URLs de descarga se generan por dos horas.

## Configuración en SSM

Las Lambdas leen la configuración desde estos parámetros de SSM Parameter
Store y la conservan en memoria durante la vida del contenedor:

- `/normativa-precheck/openai-api-key`, de tipo `SecureString`;
- `/normativa-precheck/vector-store-id`, de tipo `String`.

`make deploy_backend` comprueba que ambos parámetros existen antes de
empaquetar o crear recursos.

## Despliegue

Configura las credenciales de AWS y ejecuta:

```bash
make deploy_all
```

Variables opcionales:

```bash
export AWS_PROFILE="mi-perfil"
export AWS_REGION="eu-west-1"
export STACK_NAME="normativa-precheck"
export DOMAIN_NAME="normativa-precheck.endrokosai.com"
export HOSTED_ZONE_ID="Z02223832U2M8HYJCXSFK"
export OPENAI_API_KEY_PARAMETER="/otra/ruta/openai-api-key"
export VECTOR_STORE_ID_PARAMETER="/otra/ruta/vector-store-id"
```

Para publicar únicamente una nueva versión del frontend:

```bash
make deploy_front
```
