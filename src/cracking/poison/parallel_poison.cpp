#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <array>
#include <regex>
#include <fstream>
#include <cmath>
#include <iomanip>
#include <chrono>
#include <thread>
#include <mutex>
#include <filesystem>

using namespace std;

string PART_FILENAME = "part_";
string PART_EXTENSION = ".tmp";

mutex mtx;

template <typename T>
void debug_vector(vector<T> v, string message = ""){
    for(int i = 0; i < v.size(); i++){
        cout << message << v[i] << endl;
    }
}

void ascii_art(){
cout << endl << endl;
cout << "                █       █            ███▌                         " << endl;
cout << "               █ ██      █          █  ▐      ██████              " << endl;
cout << "              █    █      █          █ ▐     █   ▐  █             " << endl;
cout << "          █   █     █     █           █      █   ▐  █     █       " << endl;
cout << "  ████  ███  █       █     █   ▌█ █    █    █       █     █       " << endl;
cout << "  █   ██  █  █ ■   ■ █     █   █ █ ▌   ██   █ ■  ■  █     █       " << endl;
cout << "   █      █  █        █    █   ▌█ █     █  █        █    █        " << endl;
cout << "   ▌█    █   █ █    █ █    █   █▌█ ▌    █ █   ███   █   █ █      █" << endl;
cout << "   ▌ █   █   █  ████  ▌    █            █ █  █   █  █  ██ █     █ " << endl;
cout << "   ▌ █  ██   █       █▌    █          ███ █        █▌  █  █    █  " << endl;
cout << "   ▌ ▐█ █    ▌███  ██      █      ████    ▌█   ████▌  █   █   █▌  " << endl;
cout << "   ▌ ▐ ██    ▌   ██        ▐       ▐      ▌ ███    ▌ █    █  █ ▌  " << endl;
cout << "   ▌ ▐ ▌█    ▌             ▐       ▐         ▌       █    █ █     " << endl;
cout << "   ▌ ▐   █                         ▐         ▌      █▐    ██      " << endl;
cout << "          █                                  ▌     █ ▐    █       " << endl;
cout << "   ▌ ▌     █                       ▐              █       █       " << endl;
cout << "                                                          ▐       " << endl << endl;
}

string padleftzeros(int n, int qtd){
    string str = to_string(n);

    if(str.size() == qtd) return str;

    str.insert(0, qtd - str.size(), '0');
    return str;
}

int get_max_case(size_t number_sz){
    string mx = "";

    for(size_t i = 0; i < number_sz; i++){
        mx += "9";
    }

    return stoi(mx);
}

vector<string> split(string text, regex pattern){
    sregex_token_iterator iterator(text.begin(), text.end(), pattern, -1); 
    sregex_token_iterator end;

    return { iterator, end };
}

void merge_outputs(size_t cpus){
    ofstream foutput("wifi_wordlist.txt", ios::binary);

    for(size_t i = 1; i <= cpus; i++){
        string filename = PART_FILENAME + to_string(i) + PART_EXTENSION;

        ifstream part(filename, ios::binary);
        foutput << part.rdbuf();

        part.close();

        filesystem::remove(filename);
    }
}

void increment_decimal(string& value){
    for(size_t i = value.size(); i-- > 0;){
        if(value[i] < '9'){
            ++value[i];
            return;
        }

        value[i] = '0';
    }
}

void worker_process(
                size_t id,
                size_t cpus,
                long start, 
                long end, 
                size_t original_sz,
                size_t number_sz, 
                vector<string> splitted, 
                vector<array<size_t, 2>> ranges
                    ){
    string sid = to_string(id);
    string part_filename = PART_FILENAME + sid + PART_EXTENSION;
    ofstream output_part(part_filename);
    int ansi_line_diff = cpus - id;

    string padded = padleftzeros(start, number_sz);

    for(start; start <= end; start++){
        string password;
        password.reserve(original_sz);

        for(int i = 0; i < splitted.size(); i++){
            password.append(splitted[i]);

            if(i < ranges.size()){
                string_view chunk(
                    padded.data() + ranges[i][0], // inicio do range
                    ranges[i][1] // tamaho do range
                );

                password += chunk;
            }
        }

        output_part << password << "\n";

        if(start % 1000 == 0){
            lock_guard<mutex> lock(mtx);

            cout << "\033[" << to_string(ansi_line_diff) << "A";
            cout << "\r";
            cout << "[POISON] ~ Progresso: " << fixed << setprecision(2) << (double)start / end * 100.0 << "%";
            cout << "\033[" << to_string(ansi_line_diff) << "B";

            cout.flush();
        }

        increment_decimal(padded);
    }

    output_part.close();
}

size_t cpu_distribution(){
    size_t hardware_cores = thread::hardware_concurrency();

    if(hardware_cores <= 1) return 1;
    
    if(hardware_cores >= 2 && hardware_cores <= 4) return floor(hardware_cores / 2);
    if(hardware_cores > 4 && hardware_cores <= 6) return 3;

    return 4;
}

int main(){
    ascii_art();
    
    size_t KB_SZ = 1024;
    size_t MB_SZ = pow(KB_SZ, 2);
    size_t GB_SZ = pow(KB_SZ, 3);

    regex pattern(R"(\?+)"); 
    regex dot_replace(R"(\.)");
    smatch match;

    vector<size_t> chunk_sizes;
    vector<array<size_t, 2>> ranges;
    
    string text = "";
    
    cout << "[POISON] ~ Digite o padrão de senha: ";
    cin  >> text; 
    
    size_t original_sz = text.size();

    cin.ignore();

    if(!regex_search(text, match, pattern)){
        cout << endl << "[POISON] ~ Precisa informar as flags numéricas (\"?\")" << endl;
        cout << "[POISON] ~ Pressione ENTER ou qualquer tecla para sair.";

        cin.ignore();

        return 0;
    }

    size_t number_sz = 0;
    size_t offset = 0;

    for(
        sregex_iterator iterator(text.begin(), text.end(), pattern), end;
        iterator != end;
        ++iterator
    ){
        size_t size = iterator->length();

        ranges.push_back(
            {
                offset, 
                size
            }
        );

        number_sz += size;
        offset += size;
    }

    long max_case = get_max_case(number_sz) + 1;

    vector<string> splitted = split(
        regex_replace(text, pattern, "."), 
        dot_replace
    );

    cout << "CONFIGURAÇÃO:" << endl;
    cout << "[POISON] ~ Tamanho estimado do arquivo: ";

    size_t file_bytes = (text.size() + 1 ) * max_case;

    cout << fixed << setprecision(2);

    if(file_bytes <= KB_SZ)                            cout << file_bytes << "B" << endl;
    else if(file_bytes > KB_SZ && file_bytes <= MB_SZ) cout << file_bytes / KB_SZ << "KB" << endl;    
    else if(file_bytes > MB_SZ && file_bytes <= GB_SZ) cout << file_bytes / MB_SZ << "MB" << endl;
    else                                               cout << file_bytes / GB_SZ << "GB" << endl;

    size_t cpus = cpu_distribution();

    cout << "[POISON] ~ Uso de threads: " << cpus << endl << endl;

    cout << "- Pressione qualquer tecla para iniciar - ";
    cin.ignore();

    cout << endl << "[POISON] ~ Iniciando processamento..." << endl << endl;
    cout.flush();

    for (size_t i = 0; i < cpus; ++i){
        cout << "[POISON] ~ Thread " << i << ": 0.00%\n";
    }

    cout.flush();

    auto st_time = chrono::high_resolution_clock::now();
    
    size_t operations = floor(max_case / cpus);
    size_t rest_operations = max_case % cpus;

    vector<thread> threads;
    
    offset = -1;

    for(size_t i = 1; i <= cpus; i++){
        if(i == cpus){
            threads.emplace_back(
                worker_process, 
                i, 
                cpus,
                offset + 1, 
                offset + operations + rest_operations,
                original_sz,
                number_sz,
                splitted,
                ranges
            );

            break;
        }else {
            threads.emplace_back(
                worker_process, 
                i, 
                cpus,
                offset + 1, 
                offset + operations,
                original_sz,
                number_sz,
                splitted,
                ranges
            );
        }

        offset += operations;
    }

    for(size_t t = 0; t < threads.size(); t++){
        threads[t].join();
    }

    merge_outputs(cpus);

    auto end_time = chrono::high_resolution_clock::now();

    chrono::duration<double, milli> diff = end_time - st_time;

    cout << "\n\n[POISON] ~ Arquivo gerado com sucesso! (wifi-wordlist.txt)" << endl;
    cout << "[POISON] ~ Pressione ENTER ou qualquer tecla para sair." << endl;
    cout << "[POISON] ~ Finalizado em " << diff.count() / 1000 << " segundos.";

    cin.ignore();

    return 0;
}