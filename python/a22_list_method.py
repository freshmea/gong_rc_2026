def main():
    list_a = [1, 2, 3]
    list_b = [4, 5, 6]
    print(list_a + list_b)
    print(list_a)
    list_a.extend(list_b)
    print(list_a)

    list_b.append(7)
    list_b.append(8)
    print(list_b)
    list_b.insert(1, 4.5)   # type: ignore
    print(list_b)


if __name__ == "__main__":
    main()
