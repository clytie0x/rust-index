use std::io::Read;

enum Grade {
    A,
    B,
    C,
}

fn grade(score: i32) -> Grade {
    if score >= 80 {
        Grade::A
    } else if score >= 70 {
        Grade::B
    } else {
        Grade::C
    }
}

fn main() {
    let mut input = String::new();
    std::io::stdin().read_to_string(&mut input).unwrap();
    let score: i32 = input.trim().parse().unwrap();
    match grade(score) {
        Grade::A => println!("A"),
        Grade::B => println!("B"),
        Grade::C => println!("C"),
    }
}
