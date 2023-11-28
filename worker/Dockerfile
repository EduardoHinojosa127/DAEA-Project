# Utiliza la imagen oficial de .NET para SDK para construir la aplicación
FROM mcr.microsoft.com/dotnet/sdk:7.0 AS build-env

# Establece el directorio de trabajo
WORKDIR /app

# Copia los archivos del proyecto y restaura las dependencias
COPY *.csproj ./
RUN dotnet restore

# Copia el resto de la aplicación y compila
COPY . ./
RUN dotnet publish -c Release -o out

# Utiliza la imagen oficial de .NET para ASP.NET para tiempo de ejecución
FROM mcr.microsoft.com/dotnet/aspnet:7.0

# Establece el directorio de trabajo
WORKDIR /app

# Copia la salida de la compilación anterior
COPY --from=build-env /app/out .

# Comando para iniciar la aplicación
CMD ["dotnet", "worker.dll", "&", "sleep", "infinity"]
