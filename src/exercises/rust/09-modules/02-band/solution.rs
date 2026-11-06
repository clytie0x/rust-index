use std::io::Read;

mod grade {
    pub fn band(score: i32) -> &'static str {
        if score >= 80 {
            "A"
        } else if score >= 70 {
            "B"
        } else {
            "C"
        }
    }
}

use grade::band;

fn main() {
    let mut input = String::new();
    std::io::stdin().read_to_string(&mut input).unwrap();
    let score: i32 = input.trim().parse().unwrap();
    println!("{}", band(score));
}
