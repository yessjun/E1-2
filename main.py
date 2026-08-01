"""터미널에서 동작하는 사지선다 퀴즈 게임."""

import json
import os

LINE = "=" * 40
STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "state.json")


class Quiz:
    """문제 하나를 표현한다. 정답은 선택지 번호(1-4)로 관리한다."""

    def __init__(self, question, choices, answer):
        self.question = question
        self.choices = choices
        self.answer = answer

    def show(self, number):
        print(f"[문제 {number}]")
        print(self.question)
        print()
        for i, choice in enumerate(self.choices, start=1):
            print(f"{i}. {choice}")

    def is_correct(self, picked):
        return picked == self.answer

    def answer_text(self):
        return self.choices[self.answer - 1]

    def to_dict(self):
        return {"question": self.question, "choices": self.choices, "answer": self.answer}

    @staticmethod
    def from_dict(data):
        return Quiz(data["question"], data["choices"], data["answer"])


def default_quizzes():
    """저장된 데이터가 없을 때 사용하는 기본 문제. 주제는 컴퓨터 구조와 운영체제."""
    return [
        Quiz(
            "CPU가 명령어 하나를 처리하는 기본 사이클의 순서는?",
            ["해석 - 인출 - 실행", "인출 - 해석 - 실행", "실행 - 인출 - 해석", "인출 - 실행 - 해석"],
            2,
        ),
        Quiz(
            "프로그램 카운터(PC)가 담고 있는 값은?",
            [
                "직전에 실행한 명령어의 주소",
                "연산에 사용할 피연산자",
                "다음에 실행할 명령어의 주소",
                "스택의 최상단 주소",
            ],
            3,
        ),
        Quiz(
            "CPU와 주기억장치 사이에 캐시 메모리를 두는 이유는?",
            [
                "보조기억장치의 용량을 늘리기 위해",
                "두 장치의 속도 차이를 줄이기 위해",
                "전력 소비를 줄이기 위해",
                "프로세스 간에 데이터를 공유하기 위해",
            ],
            2,
        ),
        Quiz(
            "같은 프로세스에 속한 스레드들이 공유하지 않는 영역은?",
            ["코드 영역", "데이터 영역", "힙 영역", "스택 영역"],
            4,
        ),
        Quiz(
            "교착 상태가 발생하기 위한 네 가지 필요조건에 해당하지 않는 것은?",
            ["상호 배제", "점유와 대기", "선점", "순환 대기"],
            3,
        ),
        Quiz(
            "페이지 폴트가 발생했을 때 필요한 페이지를 메모리로 올리는 주체는?",
            ["운영체제", "컴파일러", "캐시 컨트롤러", "링커"],
            1,
        ),
        Quiz(
            "프레임 수를 늘렸는데 오히려 페이지 폴트가 늘어나는 현상이 나타나는 교체 알고리즘은?",
            ["FIFO", "LRU", "LFU", "OPT"],
            1,
        ),
        Quiz(
            "문맥 교환이 일어날 때 프로세스의 실행 상태를 저장해 두는 자료구조는?",
            ["TLB", "MMU", "PCB", "ALU"],
            3,
        ),
    ]


def load_state():
    """state.json 에서 퀴즈 목록과 최고 점수를 읽는다. 파일이 없으면 기본 퀴즈를 사용한다."""
    if not os.path.exists(STATE_FILE):
        return default_quizzes(), 0
    with open(STATE_FILE, encoding="utf-8") as f:
        data = json.load(f)
    quizzes = [Quiz.from_dict(item) for item in data["quizzes"]]
    print(f"저장된 데이터를 불러왔습니다. (퀴즈 {len(quizzes)}개, 최고 점수 {data['best_score']}점)")
    return quizzes, data["best_score"]


def save_state(quizzes, best_score):
    data = {"quizzes": [quiz.to_dict() for quiz in quizzes], "best_score": best_score}
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def read_text(prompt):
    """빈 문자열이 아닌 입력을 받을 때까지 다시 묻는다."""
    while True:
        raw = input(prompt).strip()
        if raw:
            return raw
        print("입력이 비어 있습니다. 다시 입력하세요.")


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


def play(quizzes):
    """등록된 퀴즈를 순서대로 출제하고 맞힌 개수를 돌려준다."""
    if not quizzes:
        print("등록된 퀴즈가 없습니다. 먼저 퀴즈를 추가하세요.")
        return None

    print()
    print(f"퀴즈를 시작합니다. (총 {len(quizzes)}문제)")
    correct = 0
    for number, quiz in enumerate(quizzes, start=1):
        print()
        print("-" * 40)
        quiz.show(number)
        print()
        picked = read_int("정답 입력: ", 1, 4)
        if quiz.is_correct(picked):
            print("정답입니다.")
            correct += 1
        else:
            print(f"오답입니다. 정답은 {quiz.answer}번 {quiz.answer_text()} 입니다.")

    total = len(quizzes)
    score = round(correct / total * 100)
    print()
    print(LINE)
    print(f"결과: {total}문제 중 {correct}문제 정답 ({score}점)")
    print(LINE)
    return correct, total, score


def add_quiz(quizzes):
    """문제, 선택지 4개, 정답 번호를 입력받아 목록에 추가한다."""
    print()
    print("새로운 퀴즈를 추가합니다.")
    print()
    question = read_text("문제를 입력하세요: ")
    choices = [read_text(f"선택지 {i}: ") for i in range(1, 5)]
    answer = read_int("정답 번호 (1-4): ", 1, 4)
    quizzes.append(Quiz(question, choices, answer))
    print()
    print("퀴즈가 추가되었습니다.")


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
    quizzes, best_score = load_state()
    while True:
        show_menu()
        choice = read_int("선택: ", 1, 5)
        if choice == 1:
            play(quizzes)
        elif choice == 2:
            add_quiz(quizzes)
            save_state(quizzes, best_score)
        elif choice == 5:
            print("게임을 종료합니다.")
            break
        else:
            print("아직 준비되지 않은 기능입니다.")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print()
        print("입력이 중단되어 게임을 종료합니다.")
