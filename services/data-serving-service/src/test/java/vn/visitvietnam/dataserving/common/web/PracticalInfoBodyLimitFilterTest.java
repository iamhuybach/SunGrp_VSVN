package vn.visitvietnam.dataserving.common.web;

import jakarta.servlet.ServletInputStream;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.mock.web.MockHttpServletRequest;
import org.springframework.mock.web.MockHttpServletResponse;

import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.nio.charset.StandardCharsets;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

class PracticalInfoBodyLimitFilterTest {

    private final PracticalInfoBodyLimitFilter filter = new PracticalInfoBodyLimitFilter();

    @Test
    @DisplayName("Content-Length vượt trần thì không đọc body")
    void fixedLengthOverLimitDoesNotReadBody() throws Exception {
        MockHttpServletRequest request = new MockHttpServletRequest("POST", "/api/v1/pois/practical_info") {
            @Override
            public long getContentLengthLong() {
                return PracticalInfoBodyLimitFilter.MAX_BYTES + 1L;
            }

            @Override
            public ServletInputStream getInputStream() {
                throw new AssertionError("body was read");
            }
        };
        MockHttpServletResponse response = new MockHttpServletResponse();
        filter.doFilter(request, response, (req, res) -> {
            throw new AssertionError("chain called");
        });
        assertThat(response.getStatus()).isEqualTo(400);
        assertThat(response.getContentAsString()).contains("ERR_BODY_TOO_LARGE");
    }

    @Test
    @DisplayName("Body chunked vượt trần thì dừng đọc")
    void chunkedOverLimitStopsReading() throws Exception {
        byte[] payload = new byte[PracticalInfoBodyLimitFilter.MAX_BYTES + 32];
        int[] read = {0};
        MockHttpServletRequest request = new MockHttpServletRequest("POST", "/api/v1/pois/practical_info") {
            @Override
            public ServletInputStream getInputStream() {
                ByteArrayInputStream input = new ByteArrayInputStream(payload);
                return new ServletInputStream() {
                    @Override
                    public boolean isFinished() {
                        return input.available() == 0;
                    }

                    @Override
                    public boolean isReady() {
                        return true;
                    }

                    @Override
                    public void setReadListener(jakarta.servlet.ReadListener readListener) {
                    }

                    @Override
                    public int read() {
                        int value = input.read();
                        if (value >= 0) {
                            read[0]++;
                        }
                        return value;
                    }

                    @Override
                    public int read(byte[] buffer, int off, int len) throws IOException {
                        int value = input.read(buffer, off, len);
                        if (value > 0) {
                            read[0] += value;
                        }
                        return value;
                    }
                };
            }

            @Override
            public long getContentLengthLong() {
                return -1;
            }
        };
        MockHttpServletResponse response = new MockHttpServletResponse();
        filter.doFilter(request, response, (req, res) -> {
            throw new AssertionError("chain called");
        });
        assertThat(response.getStatus()).isEqualTo(400);
        assertThat(read[0]).isLessThanOrEqualTo(PracticalInfoBodyLimitFilter.MAX_BYTES + 1);
        assertThat(read[0]).isLessThan(payload.length);
    }

    @Test
    @DisplayName("Body trong trần được chuyển tiếp")
    void smallBodyReachesChain() {
        MockHttpServletRequest request = new MockHttpServletRequest("POST", "/api/v1/pois/practical_info");
        request.setContent("{\"ids\":[\"a\"]}".getBytes(StandardCharsets.UTF_8));
        MockHttpServletResponse response = new MockHttpServletResponse();
        assertThatThrownBy(() -> filter.doFilter(request, response, (req, res) -> {
            throw new java.io.IOException("reached");
        })).hasMessage("reached");
    }
}
