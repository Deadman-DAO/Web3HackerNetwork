package deadmandao.util.maps;

import java.util.ArrayList;
import java.util.Hashtable;
import java.util.List;
import deadmandao.util.DBUtil;

/**
 * Created by IntelliJ IDEA.
 * User: menke
 * Date: Aug 11, 2008
 * Time: 5:40:57 PM
 * To change this template use File | Settings | File Templates.
 */
public abstract class SelfConstructingThreadMapWithExpiration<TYPEB> {
    public abstract TYPEB construct();
    public abstract long getLifespan();
    public abstract void dontUseSelfConstructingThreadMapWithExpirationUseTheIdleVersion();
    protected final Hashtable<Thread,HalfLifeObject> map = new Hashtable<Thread,HalfLifeObject>();
//    ScheduledThreadPoolExecutor sched = new ScheduledThreadPoolExecutor(1);

    public TYPEB remove(Thread key) {
        TYPEB retVal = null;
        HalfLifeObject hlo = null;
        synchronized (map) {
            hlo = map.remove(key);
        }
        if (hlo != null) {
            retVal = hlo.getContainedObject();
        }
        return retVal;
    }
    public SelfConstructingThreadMapWithExpiration() {
//        sched.scheduleWithFixedDelay(new Cleaner(), 30, 30, TimeUnit.SECONDS);
    }
    private class Cleaner implements Runnable {
        public void run() {
            try {
                List<Thread> remove = new ArrayList<Thread>();
                List<HalfLifeObject> destroy = new ArrayList<HalfLifeObject>();
                synchronized(map) {
                    for ( Thread x : map.keySet() ) {
                        HalfLifeObject hlo = map.get(x);
                        if ( hlo.isExpired() ) {
                            remove.add(x);
                        }
                    }
                }
                synchronized (map) {
                    for ( Thread x : remove ) {
                        HalfLifeObject hlo = map.remove(x);
                        if (hlo != null) {
                            destroy.add(hlo);
                        }
                    }
                }
                for ( HalfLifeObject hlo : destroy ) {
                    hlo.close();
                }
            } catch (Throwable t) {
                t.printStackTrace();
            }
        }
    }

    protected class HalfLifeObject {
        TYPEB blood;
        long expirationTime;
        public HalfLifeObject( TYPEB b ) {
            blood = b;
            expirationTime = System.currentTimeMillis() + getLifespan();
        }
        public boolean isExpired() {
            return expirationTime < System.currentTimeMillis();
        }
        public TYPEB getContainedObject() {
            return blood;
        }
        public void close() {
            DBUtil.closeAnything(blood);            
        }
    }
    public TYPEB getIt() {
        Thread a = Thread.currentThread();
        HalfLifeObject hlo = map.get(a);
        if ( hlo == null || hlo.isExpired() ) {
            if ( hlo != null ) {
                hlo.close();
            }
            hlo = new HalfLifeObject(construct());
            synchronized(map) {
                map.put(a, hlo);
            }
        }

        return hlo.getContainedObject();
    }
}
