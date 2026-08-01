"""터미널에서 동작하는 사지선다 퀴즈 게임."""

LINE = "=" * 40


def read_int(prompt, low, high):
    """low 이상 high 이하의 정수를 받을 때까지 다시 묻는다."""
    while True:
        raw = input(prompt).strip()
        if not raw:
            print(f"입력이 비어 있습니다. {low}-{high} 사이의 숫자를 입력하세요.")
            continue
        try:
            value = int(raw)
        except ValueError:
            print(f"잘못된 입력입니다. {low}-{high} 사이의 숫자를 입력하세요.")
            continue
        if not low <= value <= high:
            print(f"잘못된 입력입니다. {low}-{high} 사이의 숫자를 입력하세요.")
            continue
        return value


def show_menu():
    print()
    print(LINE)
    print("           나만의 퀴즈 게임")
    print(LINE)
    print("1. 퀴즈 풀기")
    print("2. 퀴즈 추가")
    print("3. 퀴즈 목록")
    print("4. 점수 확인")
    print("5. 종료")
    print(LINE)


def main():
    while True:
        show_menu()
        choice = read_int("선택: ", 1, 5)
        if choice == 5:
            print("게임을 종료합니다.")
            break
        print("아직 준비되지 않은 기능입니다.")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print()
        print("입력이 중단되어 게임을 종료합니다.")
