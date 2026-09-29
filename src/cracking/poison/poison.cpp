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
//#include <thread>
//#include <mutex>
//#include <filesystem>

using namespace std;

//string PART_FILENAME = "part_";
//string PART_EXTENSION = ".tmp";

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

void increment_decimal(string& value){
    for(size_t i = value.size(); i-- > 0;){
        if(value[i] < '9'){
            ++value[i];
            return;
        }

        value[i] = '0';
    }
}

int main(){
    ascii_art();
    cout << "Gerador de wordlists de senhas single-thread. Deduz totas possibilidades numéricas possiveis de um padrão de senha informado." << endl;
    cout << "Extremamente simples: informe apenas a senha, e onde for numero, insira \"?\"." << endl << endl;
    cout << "Exemplo: senha@????" << endl << endl;
    cout << "~ E ai, deixe a mágica acontecer ^_- ~" << endl;

    cout << "AVISO: para entradas de senhas contendo a partir 8 ocorrencias de digitos (\"?\"), o processamento pode ser bem demorado e o arquivo pode passar facilmente de 2GB." << endl << endl;
    
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

    cout << "[POISON] ~ Tamanho estimado do arquivo: ";

    size_t file_bytes = (text.size() + 1 ) * max_case;

    cout << fixed << setprecision(2);

    if(file_bytes <= KB_SZ)                            cout << file_bytes << "B" << endl;
    else if(file_bytes > KB_SZ && file_bytes <= MB_SZ) cout << file_bytes / KB_SZ << "KB" << endl;    
    else if(file_bytes > MB_SZ && file_bytes <= GB_SZ) cout << file_bytes / MB_SZ << "MB" << endl;
    else                                               cout << file_bytes / GB_SZ << "GB" << endl;

    cout << endl << "[POISON] ~ Iniciando processamento..." << endl << endl;
    cout.flush();

    cout.flush();

    auto st_time = chrono::high_resolution_clock::now();

    string padded = padleftzeros(0, number_sz);
    ofstream output("poison-wordlist.txt");

    for(size_t start = 0; start <= max_case; start++){
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

        output << password << "\n";

        if(start % 1000 == 0){
            cout << "\r[POISON] ~ Progresso: " << fixed << setprecision(2) << (double)start / max_case * 100.0 << "%";
        }

        increment_decimal(padded);
    }

    auto end_time = chrono::high_resolution_clock::now();

    chrono::duration<double, milli> diff = end_time - st_time;
    output.close();

    cout << "\n\n[POISON] ~ Arquivo gerado com sucesso! (poison-wordlist.txt)" << endl;
    cout << "[POISON] ~ Pressione ENTER ou qualquer tecla para sair." << endl;
    cout << "[POISON] ~ Finalizado em " << diff.count() / 1000 << " segundos.";

    cin.ignore();

    return 0;
}