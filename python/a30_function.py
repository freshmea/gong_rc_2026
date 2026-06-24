def print_hello(a: int, value: str | int) -> str:
    """이 함수는 수업에서 작성한 예시 함수

    Args:
        a (int): 반복하는 횟수
        value (str): 추가 프린트할 데이터

    Returns:
        str: 성공 여부
    """
    for i in range(a):
        print("안녕하세요!", value, i)
    if isinstance(value, int):  # python 에서 type 을 체크 할때!!
        for _ in range(value):
            print("test")
    return "execution OK!"


def main():
    re = print_hello(3, 2)    # type hint, positional argument
    print(re)


if __name__ == "__main__":
    main()
