package deadmandao.util.maps;

import java.util.HashMap;
import java.util.Hashtable;
import java.util.Map;

/**
 * Created with IntelliJ IDEA.
 * User: menke
 * Date: 5/16/12
 * Time: 3:11 PM
 * To change this template use File | Settings | File Templates.
 */
public abstract class SelfConstructingMapMap<TYPEA,TYPEB,TYPEC> extends Hashtable<TYPEA,Map<TYPEB,TYPEC>> {
    public Map<TYPEB,TYPEC> put( TYPEA a, TYPEB b, TYPEC c ) {
        Map<TYPEB,TYPEC> retVal = get( a );
        if ( retVal == null ) {
            retVal = new HashMap<TYPEB,TYPEC>();
            super.put( a, retVal );
        }
        retVal.put(b,c);
        return retVal;
    }
    public Map<TYPEB,TYPEC> getIt(TYPEA a) {
        return super.get(a);
    }
    public TYPEC getIt( TYPEA a, TYPEB b ) {
        Map<TYPEB,TYPEC> map = super.get(a);
        TYPEC retVal = null;
        if (map == null) {
            map = new HashMap<TYPEB, TYPEC>();
            put(a, map);
        }
        retVal = map.get(b);
        if (retVal == null) {
            retVal = construct();
            map.put(b, retVal);
        }
        return retVal;
    }
    public abstract TYPEC construct();
}
