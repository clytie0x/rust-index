use std::io::Read;
use std::sync::{Arc, Mutex};
use std::thread;

fn main() {
    let mut input = String::new();
    std::io::stdin().read_to_string(&mut input).unwrap();
    let n: i32 = input.trim().parse().unwrap();
    let total = Arc::new(Mutex::new(0));
    let mut handles = Vec::new();
    for _ in 0..n {
        let total = Arc::clone(&total);
        handles.push(thread::spawn(move || {
            let mut slot = total.lock().unwrap();
            *slot += 1;
        }));
    }
    for handle in handles {
        handle.join().unwrap();
    }
    println!("{}", *total.lock().unwrap());
}
