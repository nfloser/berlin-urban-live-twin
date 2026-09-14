FROM eclipse-temurin:21-jre-alpine

ARG JENA_VERSION=6.2.0

RUN apk add --no-cache curl \
    && mkdir -p /fuseki/databases/twin \
    && curl --fail --location --retry 3 \
       "https://repo1.maven.org/maven2/org/apache/jena/jena-fuseki-server/${JENA_VERSION}/jena-fuseki-server-${JENA_VERSION}.jar" \
       --output /fuseki/fuseki.jar

WORKDIR /fuseki

EXPOSE 3030

HEALTHCHECK --interval=10s --timeout=3s --start-period=10s --retries=6 \
    CMD curl --fail --silent http://localhost:3030/$/ping >/dev/null || exit 1

CMD ["java", "-Xms256m", "-Xmx1024m", "-jar", "/fuseki/fuseki.jar", "--update", "--loc=/fuseki/databases/twin", "/twin"]
