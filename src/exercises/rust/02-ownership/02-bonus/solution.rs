use std::io::BufRead;

fn add_bonus(score: &mut i32) {
    *score += 5;
}

fn main() {
    let mut line = String::new();
    std::io::stdin().lock().read_line(&mut line).unwrap();
    let mut score: i32 = line.trim().parse().unwrap();
    add_bonus(&mut score);
    println!("{score}");
}
