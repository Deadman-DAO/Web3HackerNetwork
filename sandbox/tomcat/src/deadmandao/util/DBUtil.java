package deadmandao.util;


import java.io.Closeable;
import deadmandao.util.maps.SelfConstructingKeyDependentMap;
import java.sql.*;
import java.lang.reflect.Method;
import java.util.List;
import java.util.GregorianCalendar;
import java.math.BigDecimal;
import javax.xml.datatype.DatatypeFactory;
import javax.xml.datatype.DatatypeConfigurationException;
import javax.xml.datatype.XMLGregorianCalendar;
import javax.xml.datatype.DatatypeConstants;

public class DBUtil {

    private static final Method EVERYBODY_HAS_THIS_METHOD;

    private static final DatatypeFactory factoryFactoryFactory;

    static {
        try {
            factoryFactoryFactory = DatatypeFactory.newInstance();
        } catch(DatatypeConfigurationException dfe) {
            throw new ExceptionInInitializerError(dfe);
        }
    }

    static {
        try {
            EVERYBODY_HAS_THIS_METHOD = Object.class.getDeclaredMethod("toString");
        } catch (Exception e) {
            throw new RuntimeException("WTF? I can't find the 'toString' method on Object?", e);
        }
    }

    public static void closeResultSet(ResultSet rs) {
        try {
            if(rs != null) {
                rs.close();
            }
        } catch(SQLException sex) {
            //nothing to do
        }
    }

    public static void closeStatement(Statement stmt) {
        try {
            if(stmt != null) {
                stmt.close();
            }
        } catch(SQLException sex) {
            //nothing to do
        }
    }

    public static void closeConnection(Connection con) {
        try {
            if(con != null) {
                con.close();
            }
        } catch(SQLException sex) {
            //nothing to do
        }
    }

    public static Integer nillableInt(ResultSet rs, int index) throws SQLException {
        Integer val = null;
        int tmp = rs.getInt(index);
        if(!rs.wasNull()) {
            val = Integer.valueOf(tmp);
        }
        return val;
    }

    public static Boolean nillableBoolean(ResultSet rs, int index) throws SQLException {
        Boolean val = null;
        boolean tmp = rs.getBoolean(index);
        if(!rs.wasNull()) {
            val = Boolean.valueOf(tmp);
        }
        return val;
    }

    public static String constructInParameter(int size) {
        final StringBuilder parameter = new StringBuilder();
         for (int i = 0; i < size; i++) {
             if (i > 0) {
                 parameter.append(',');
             }
             parameter.append('?');
         }
         return parameter.toString();
    }


    public static class InClauseAndBinds<V> {
        private String inClause;
        private List<V> values;

        public InClauseAndBinds(String inClause, List<V> values) {
            this.inClause = inClause;
            this.values = values;
        }

        public List<V> getValues() {
            return values;
        }

        public String getInClause() {
            return inClause;
        }
    }

    public static class QueryBind {
        private final String query;
        private final List<BindVal> vals;

        public QueryBind(String query, List<BindVal> vals) {
            this.query = query;
            this.vals = vals;
        }

        public String getQuery() {
            return query;
        }

        public List<BindVal> getVals() {
            return vals;
        }
    }

    public static class BindVal<V> {
        private final int type; //sqlType
        private final V value;

        public BindVal(int type, V value) {
            this.type = type;
            this.value = value;
        }

        public int getType() {
            return type;
        }

        public V getValue() {
            return value;
        }
    }

    private abstract static class MethodFinder extends SelfConstructingKeyDependentMap<Class,Method> {
        abstract String getMethodName();
        public Method construct(Class x) {
            Method oneKitty = EVERYBODY_HAS_THIS_METHOD; // See Clash "Ghetto Defendant"
            try {
                oneKitty = x.getMethod(getMethodName());
//                oneKitty.setAccessible(true);
            } catch ( Exception ex ) {
                Class b = x;
                while ( b != null && oneKitty == null ) {
                    try {
                        oneKitty = b.getMethod( getMethodName() );
                    } catch ( NoSuchMethodException nsme ) {
                        b = b.getSuperclass();
                    }
                }
            }
            return oneKitty;
        }
    }
    private static final MethodFinder closerMap = new MethodFinder() {
        String getMethodName() {
            return "close";
        }
    };
    private static final MethodFinder rollbackMap = new MethodFinder() {
        String getMethodName() {
            return "rollback";
        }
    };

    public static void rollback( Connection... cons ) {
        if ( cons != null && cons.length > 0 ) {
            for ( Connection con : cons ) {
                try {
                    con.rollback();
                } catch (Throwable t) {
                    //eat it
                }
            }
        }
    }
    public static void closeAnything( Object... oa ) {
        if ( oa != null && oa.length > 0 ) {
            for ( Object o : oa ) {
                if ( o != null ) {
                    try {
                        if (Closeable.class.isAssignableFrom(o.getClass())) {
                            ((Closeable)o).close();
                        } else {
                            Method meth = closerMap.getIt(o.getClass());
                            meth.invoke(o);
                        }
                    } catch ( Throwable t ) {
                        t.printStackTrace();
                    }
                }
            }
        }
    }

    public static Integer trimAndParsePreserveNull(String s) {
        Integer retVal = null;
        try {
            retVal = s == null ? null : s.trim().length() > 0 ? Integer.parseInt(s.trim()) : null;
        } catch (NumberFormatException nfe) {
            //Just return null
        }
        return retVal;
    }
    public static String trimPreserveNull(String s) {
        return s == null || s.trim().equals("") ? null : s.trim();
    }

    public static String trim(String s) {
        return s == null ? "" : s.trim();
    }

//    public static Integer preserveNullInt( String s ) {
//        Integer retVal = null;
//        if ( s != null ) {
//            s = trim(s);
//            try {
//                retVal = Integer.parseInt(s);
//            } catch ( NumberFormatException nfe ) {
//                nfe.printStackTrace();
//            }
//        }
//        return retVal;
//    }
//
//    public static Boolean preserveNullBoolean( String s ) {
//        Boolean retVal = null;
//        if ( s != null ) {
//            s = trim(s);
//            try {
//                retVal = Integer.parseInt(s) == 1;
//            } catch ( NumberFormatException nfe ) {
//                nfe.printStackTrace();
//            }
//        }
//        return retVal;
//    }

    public static BigDecimal formatMonetary(BigDecimal val) {
        BigDecimal dollars = BigDecimal.ZERO;
        if(val != null) {
            try {
                dollars = val.setScale(2);
            } catch(ArithmeticException ae) {
                throw new RuntimeException("Unexpected money value [" + val + "].  Maximum of 2 decimal digits allowed");
            }
        }
        return dollars;
    }

    public static BigDecimal formatCredits(BigDecimal val) {
        return formatMonetary(val);
    }

    public static BigDecimal formatGPA(BigDecimal val) {
        return formatMonetary(val);
    }

    public static XMLGregorianCalendar getCurrentDate() {
        return factoryFactoryFactory.newXMLGregorianCalendar(new GregorianCalendar());
    }

    public static XMLGregorianCalendar getDate(GregorianCalendar calendar) {
        return factoryFactoryFactory.newXMLGregorianCalendar(calendar);
    }

    public static XMLGregorianCalendar toDate(long time) {
        return toDate(new java.util.Date(time));
    }

    public static XMLGregorianCalendar toDate(java.sql.Date date) {
        return toDate((java.util.Date)date);
    }

    public static XMLGregorianCalendar toDate(java.util.Date date) {
        XMLGregorianCalendar xgc = null;
        if(date != null) {
            GregorianCalendar gc = new GregorianCalendar();
            gc.setTime(date);
            xgc = factoryFactoryFactory.newXMLGregorianCalendar(gc);
        }
        return xgc;
    }

    public static XMLGregorianCalendar toDate(java.util.Date date, boolean suppressTimezone) {
        XMLGregorianCalendar cal = toDate(date);
        if(cal != null && suppressTimezone) {
            cal.setTimezone(DatatypeConstants.FIELD_UNDEFINED);
        }
        return cal;
    }

    public static java.sql.Date toSQLDate(XMLGregorianCalendar xmlCal) {
        if (xmlCal == null) {
            return null;
        } else {
            GregorianCalendar gc = xmlCal.toGregorianCalendar();
            return new java.sql.Date(gc.getTimeInMillis()); 
        }
    }

    public static Timestamp toSQLTimestamp(XMLGregorianCalendar xmlCal) {
        if (xmlCal == null) {
            return null;
        } else {
            GregorianCalendar gc = xmlCal.toGregorianCalendar();
            return new java.sql.Timestamp(gc.getTimeInMillis()); 
        }
    }

    public static void setInt( PreparedStatement ps, int index, Integer nullableValue ) throws SQLException {
        if ( ps == null ) {
            throw new SQLException("PreparedStatement is NULL!");
        }
        if ( nullableValue == null ) {
            ps.setNull( index, Types.INTEGER );
        } else {
            ps.setInt( index, nullableValue.intValue() );
        }
    }
    public static void setBoolean( PreparedStatement ps, int index, Boolean nullableValue ) throws SQLException {
        if ( ps == null ) {
            throw new SQLException("PreparedStatement is NULL!");
        }
        if ( nullableValue == null ) {
            ps.setNull( index, Types.BIT );
        } else {
            ps.setBoolean( index, nullableValue.booleanValue() );
        }
    }
    public static void setString( PreparedStatement ps, int index, String nullableValue ) throws SQLException {
        if ( ps == null ) {
            throw new SQLException("PreparedStatement is NULL!");
        }
        if ( nullableValue == null ) {
            ps.setNull( index, Types.VARCHAR );
        } else {
            ps.setString(index, nullableValue );
        }
    }

   public static Timestamp toTimestamp(XMLGregorianCalendar cal) {
        if(cal == null)
           return (Timestamp)null;
       
        GregorianCalendar gc = cal.toGregorianCalendar();
        return new Timestamp(gc.getTimeInMillis());
    }
   public static void setTimestamp( PreparedStatement ps, int index, Timestamp nullableValue ) throws SQLException {
        if ( ps == null ) {
            throw new SQLException("PreparedStatement is NULL!");
        }
        if ( nullableValue == null ) {
            ps.setNull( index, Types.TIMESTAMP );
        } else {
            ps.setTimestamp(index, nullableValue );
        }
    }

}
