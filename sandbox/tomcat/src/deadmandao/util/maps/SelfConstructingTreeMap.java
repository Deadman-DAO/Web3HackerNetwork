package deadmandao.util.maps;

import java.util.TreeMap;

public abstract class SelfConstructingTreeMap<TYPEA,TYPEB> extends TreeMap<TYPEA,TYPEB> {
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
