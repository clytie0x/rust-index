use std::io::Read;

struct Student {
    name: String,
    math: i32,
    science: i32,
}

impl Student {
    fn average(&self) -> i32 {
        (self.math + self.science) / 2
    }
}

fn main() {
    let mut input = String::new();
    std::io::stdin().read_to_string(&mut input).unwrap();
    let mut parts = input.split_whitespace();
    let student = Student {
        name: parts.next().unwrap().to_string(),
        math: parts.next().unwrap().parse().unwrap(),
        science: parts.next().unwrap().parse().unwrap(),
    };
    println!("{} {}", student.name, student.average());
}
