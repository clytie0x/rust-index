use std::io::Read;

trait Summary {
    fn summary(&self) -> String;
}

struct Student {
    name: String,
    score: i32,
}

impl Summary for Student {
    fn summary(&self) -> String {
        format!("{} {}", self.name, self.score)
    }
}

fn main() {
    let mut input = String::new();
    std::io::stdin().read_to_string(&mut input).unwrap();
    let mut parts = input.split_whitespace();
    let student = Student {
        name: parts.next().unwrap().to_string(),
        score: parts.next().unwrap().parse().unwrap(),
    };
    println!("{}", student.summary());
}
