package deadmandao.util.maps;

import java.util.Hashtable;

public abstract class SelfConstructingMap<TYPEA,TYPEB> extends Hashtable<TYPEA,TYPEB> {
    public abstract TYPEB construct();
    public TYPEB getIt(TYPEA a) {
        TYPEB b = get(a);
        if ( b == null ) {
            b = construct();
            put(a, b);
        }
        return b;
    }
}
