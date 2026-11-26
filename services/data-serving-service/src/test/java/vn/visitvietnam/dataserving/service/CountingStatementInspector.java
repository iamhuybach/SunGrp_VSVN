package vn.visitvietnam.dataserving.service;

import org.hibernate.resource.jdbc.spi.StatementInspector;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.concurrent.atomic.AtomicInteger;

public class CountingStatementInspector implements StatementInspector {

    public static final AtomicInteger COUNT = new AtomicInteger();
    public static final List<String> SQL = Collections.synchronizedList(new ArrayList<>());

    public static void reset() {
        COUNT.set(0);
        SQL.clear();
    }

    @Override
    public String inspect(String sql) {
        COUNT.incrementAndGet();
        SQL.add(sql);
        return sql;
    }
}
