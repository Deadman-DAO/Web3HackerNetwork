package deadmandao.util.maps;

/**
 * Created with IntelliJ IDEA.
 * User: menke
 * Date: 11/1/12
 * Time: 11:16 AM
 * To change this template use File | Settings | File Templates.
 */
public abstract class SelfConstructingThreadMapWithIdleExpiration<TYPEB> extends SelfConstructingThreadMapWithExpiration<TYPEB> {
    public TYPEB getIt() {
        Thread a = Thread.currentThread();
        HalfLifeObject hlo = map.get(a);
        if ( hlo == null || hlo.isExpired() ) {
            if ( hlo != null ) {
                hlo.close();
            }
            TYPEB thing = construct();
            if ( thing != null ) {
                hlo = new HalfLifeObject(thing);
                synchronized (map) {
                    map.put(a, hlo);
                }
            }
        }
        hlo.expirationTime = System.currentTimeMillis() + getLifespan();
        return hlo.getContainedObject();
    }

    @Override
    public void dontUseSelfConstructingThreadMapWithExpirationUseTheIdleVersion() {
        // Having an asynchronous thread close an active object after a fixed period of time causes all sorts of problems
        // Maybe in the future just set a flag for object-in-use and only close it if it synchronized(notOpen)
    }
}
