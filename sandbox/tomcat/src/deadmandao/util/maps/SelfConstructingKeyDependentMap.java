package deadmandao.util.maps;

import java.util.Hashtable;


public abstract class SelfConstructingKeyDependentMap<TYPEA,TYPEB> extends Hashtable<TYPEA,TYPEB> {
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