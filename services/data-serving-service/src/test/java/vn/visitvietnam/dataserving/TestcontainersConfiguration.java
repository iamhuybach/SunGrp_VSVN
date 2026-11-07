package vn.visitvietnam.dataserving;

import org.springframework.boot.test.context.TestConfiguration;
import org.springframework.boot.testcontainers.service.connection.ServiceConnection;
import org.springframework.context.annotation.Bean;
import org.testcontainers.postgresql.PostgreSQLContainer;
import org.testcontainers.utility.DockerImageName;
import org.testcontainers.utility.MountableFile;

@TestConfiguration(proxyBeanMethods = false)
public class TestcontainersConfiguration {

	@Bean
	@ServiceConnection
	public PostgreSQLContainer postgresContainer() {
		return new PostgreSQLContainer(DockerImageName.parse("postgres:18-alpine").asCompatibleSubstituteFor("postgres"))
				.withCopyFileToContainer(MountableFile.forClasspathResource("db/00_create_schema_apps.sql"),
						"/docker-entrypoint-initdb.d/00_create_schema_apps.sql")
				.withCopyFileToContainer(MountableFile.forClasspathResource("gld_srv_serve.pg.sql"),
						"/docker-entrypoint-initdb.d/10_gld_srv_serve.sql");
	}

}

