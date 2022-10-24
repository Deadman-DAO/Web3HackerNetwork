from concurrent.futures import ThreadPoolExecutor
from log_trial import log


def main():
    print("Interdependencies?!?")

    config_dict= {}
    future_list = []
    with ThreadPoolExecutor() as tpe:
        for n in range(1, 100):
            future_list.append(
                tpe.submit(exec, compile('import import_context_test as i\nfrom log_trial import log\nlog(("I am here", i.get_my_variable()))', 'wtf', 'exec'), config_dict))
            future_list.append(
                tpe.submit(exec, compile(
                    'import import_context_test as i\nfrom log_trial import log\nlog(("You are not here", i.get_my_variable()))',
                    'wtf', 'exec'), config_dict))
        for few in future_list:
            result = few.result()
            if result:
                log("Result:", result)

    log("I'm leaving!")


if __name__ == '__main__':
    main()
