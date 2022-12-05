package deadmandao.util.maps;

import java.lang.reflect.Method;
import java.util.HashMap;
import java.util.Map;


public class MethodFinder {
    private static final Method EVERYBODY_HAS_THIS_METHOD;

    static {
        try {
            EVERYBODY_HAS_THIS_METHOD = Object.class.getDeclaredMethod("toString");
        } catch (Exception e) {
            throw new RuntimeException("WTF? I can't find the 'toString' method on Object?", e);
        }
    }
    private static class SingleMethodFinder extends SelfConstructingKeyDependentMap<Class, Method> {
        String methodName;
        public SingleMethodFinder(String methodName) {
            this.methodName = methodName;
        }
        public String getMethodName() {
            return methodName;
        }
        public Method construct(Class x) {
            Method oneKitty = EVERYBODY_HAS_THIS_METHOD; // See Clash "Ghetto Defendant"
            try {
                oneKitty = x.getMethod(getMethodName());
                oneKitty.setAccessible(true);
            } catch ( Exception ex ) {
                Class b = x;
                while ( b != null && oneKitty == null ) {
                    try {
                        oneKitty = b.getDeclaredMethod( getMethodName() );
                        oneKitty.setAccessible(true);
                    } catch ( NoSuchMethodException nsme ) {
                        b = b.getSuperclass();
                    }
                }
            }

            return oneKitty;
        }
    }
    private static Map<String, SingleMethodFinder> MethodNameToMethodFinderMap = new HashMap<String, SingleMethodFinder>();

    public static Method getIt( Class type, String method ) {
        SingleMethodFinder finder = MethodNameToMethodFinderMap.get(method);
        if ( finder == null ) {
            finder = new SingleMethodFinder(method);
            MethodNameToMethodFinderMap.put( method, finder );
        }
        return finder.getIt(type);
    }

    public static Method getIt( String clsName, String method ) {
        Method meth = null;

        try {
            Class c = Class.forName(clsName);
        } catch ( ClassNotFoundException cnfe ) {
            
        }
        return meth;
    }
}
