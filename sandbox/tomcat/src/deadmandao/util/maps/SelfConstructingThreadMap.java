package deadmandao.util.maps;

public abstract class SelfConstructingThreadMap<TYPE> extends SelfConstructingMap<Thread,TYPE> {
    public TYPE getIt() {
        return getIt(Thread.currentThread());
    }
}
