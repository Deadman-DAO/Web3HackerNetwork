package deadmandao.util.maps;

import java.util.Hashtable;
import java.util.List;

/**
 * Created with IntelliJ IDEA.
 * User: menke
 * Date: 5/16/12
 * Time: 3:11 PM
 * To change this template use File | Settings | File Templates.
 */
public class SelfConstructingCollectionMap<TYPEA,TYPEB> extends Hashtable<TYPEA,List<TYPEB>> {
//    public List<TYPEB> put( TYPEA a, TYPEB b ) {
//        List<TYPEB> retVal = get( a );
//        if ( retVal == null ) {
//            retVal = new ArrayList<TYPEB>();
//            super.put( a, retVal );
//        }
//        retVal.add(b);
//        return retVal;
//    }
//    public List<TYPEB> getIt(TYPEA a) {
//        return super.get(a);
//    }
}
