package deadmandao.util.maps;

import java.util.TreeMap;


public abstract class SelfConstructingKeyDependentTreeMap<TYPEA,TYPEB> extends TreeMap<TYPEA,TYPEB> {
    public abstract TYPEB construct(TYPEA a);
    public TYPEB getIt(TYPEA a) {
        TYPEB b = get(a);
        if ( b == null ) {
            b = construct(a);
            put(a, b);
        }
        return b;
    }
}