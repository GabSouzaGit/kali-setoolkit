#include <iostream>
#include <string>
#include <vector>
#include <regex>
#include <fstream>
#include <cmath>
#include <iomanip>

using namespace std;

template <typename T>
void debug_vector(vector<T> v, string message = ""){
    for(int i = 0; i < v.size(); i++){
        cout << message << v[i] << endl;
    }
}

int reduce(vector<size_t> x){
    int sum = 0;

    for(int i = 0; i < x.size(); i++){
        sum += x[i];
    }

    return sum;
}

string padleftzeros(int n, int qtd){
    string str = to_string(n);

    while(str.size() < qtd){
        str = "0" + str;
    }

    return str;
}

vector<string> chunk(string n, vector<size_t> chunks_sizes){
    //size_t CHUNK_SIZE = 2;

    vector<string> chunks = {};
    string chunk = "";

    int chunk_sz_counter = 0;
    int chunk_sz_index = 0;
    size_t chunk_sz = chunks_sizes[chunk_sz_index];

    for(int i = 0; i < n.size(); i++){
        if((chunk_sz_counter == chunk_sz) || i == n.size() - 1){

            if(chunk_sz_index == chunks_sizes.size() - 1) {
                chunk += n[i];
                chunks.push_back(chunk);

                break;
            }else {
                chunks.push_back(chunk);
                
                chunk = n[i];

                chunk_sz_counter = 1;
    
                chunk_sz_index++;
                chunk_sz = chunks_sizes[chunk_sz_index];
            }
        }else{
            chunk += n[i];
            chunk_sz_counter++;
        }
    }

    return chunks;
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

int main(){
 cout << "▌██           ▌██      ▌█          ▌██        ▌██        ▌██         █" << endl;
cout << "▌████          ▌███     ▌█         ▌██        ▌█████      ▌██         █" << endl;
cout << "▌█  ██        ▌█   █    ▌██       ▌██        ▌██   ██     ▌██         █" << endl;
cout << "▌█   ██      ▌█     █    ▌██     ▌██         ▌█     ██     ▌█        ██" << endl;
cout << "▌█    ███   ▌██      █     ▌█    ▌█         ▌█       █     ▌██       █ " << endl;
cout << "▌█      ███▌██       █     ▌█    ▌██        ▌█        █     ▌█       █ " << endl;
cout << "▌█      ███▌█        █     ▌█     ▌██      ▌█         █     ▌█       █ " << endl;
cout << "▌█   ███   ▌█        █     ▌██      ▌██    ▌█         █     ▌██    ▌██ " << endl;
cout << "▌█  ██     ▌█        █     ▌██       ▌██   ▌█          █    ▌██    ▌█  " << endl;
cout << "▌█  █      ▌█        █     ▌██        ▌█   ▌█          █    ▌█ █   ▌█  " << endl;
cout << " ▌███      ▌█        █     ▌██        ▌██  ▌█          █    ▌█ █   ██  " << endl;
 cout << "▌██       ▌█       █      ▌██         ▌█  ▌█          █    ▌█ ▌█  █   " << endl;
  cout << "▌█       ▌█      ██      ▌██        ▌██  ▌█          █    ▌█ ▌██ █   " << endl;
  cout << "▌█       ▌█      █      ▌██         ▌█▌  ▌█          █    ▌▌ ▌ █ █   " << endl;
  cout << "▌█       ▌██    █      ▌██         ▌██▌  ▌█         █    ▌█▌ ▌ ███   " << endl;
   cout << "▌█       ▌█   ██     ▌██         ▌██ ▌  ▌██       ██    ▌█▌    ██   " << endl;
   cout << "▌█       ▌██ ██     ▌██         ▌██  ▌   ▌███    ██▌   ▌█ ▌     █   " << endl;
    cout << "▌█       ▌███      ▌█          ▌█         ▌██████ ▌   ██       ▌   " << endl;
     cout << "▌         ▌        ▌           ▌         ▌▌          ▌        ▌   " << endl;
      cout << "         ▌                    ▌         ▌           ▌        ▌   " << endl;
       cout << "                             ▌         ▌           ▌            " << endl;
        cout << "                            ▌                     ▌            " << endl << endl;

    size_t KB_SZ = 1024;
    size_t MB_SZ = pow(KB_SZ, 2);
    size_t GB_SZ = pow(KB_SZ, 3);

    ofstream file("wifi-wordlist.txt");

    if(!file.is_open()){
        cerr << "Falha ao inicializar arquivo de senhas.";
        cin.ignore();

        return 1;
    }

    regex pattern(R"(\?+)"); 
    regex dot_replace(R"(\.)");
    string text = "";
    vector<size_t> chunk_sizes = {};
    smatch match;

    cout << "[POISON] ~ Digite o padrão de senha: ";
    cin  >> text; 

    cin.ignore();

    if(!regex_search(text, match, pattern)){
        cout << endl << "[POISON] ~ Precisa informar as flags numéricas (\"?\")" << endl;
        cout << "[POISON] ~ Pressione ENTER ou qualquer tecla para sair.";

        cin.ignore();

        return 0;
    }

    for(
        sregex_iterator iterator(text.begin(), text.end(), pattern), end;
        iterator != end;
        ++iterator
    ){
        chunk_sizes.push_back(iterator->length());
    }


    size_t number_sz = reduce(chunk_sizes);
    int max_case = get_max_case(number_sz);

    string placeholders_replaced = regex_replace(text, pattern, ".");

    vector<string> splitted = split(placeholders_replaced, dot_replace);

    cout << endl << "[POISON] ~ Iniciando iteração..." << endl;
    cout << "[POISON] ~ Tamanho estimado do arquivo: ";

    size_t file_bytes = (text.size() + 1 ) * max_case;

    cout << fixed << setprecision(2);

    if(file_bytes <= KB_SZ){
        cout << file_bytes << "B" << endl;
    }
    else if(file_bytes > KB_SZ && file_bytes <= MB_SZ){
        cout << file_bytes / KB_SZ << "KB" << endl;
    }
    else if(file_bytes > MB_SZ && file_bytes <= GB_SZ){
        cout << file_bytes / MB_SZ << "MB" << endl;
    }else {
        cout << file_bytes / GB_SZ << "GB" << endl;
    }

    for(int number = 0; number <= max_case; number++){
        string padded = padleftzeros(number, number_sz);
        vector<string> chunks = chunk(padded, chunk_sizes);
        string password = "";

        for(int ispt = 0; ispt < splitted.size(); ispt++){
            password += splitted[ispt];

            if(ispt < chunks.size()){
                password += chunks[ispt];
            }
        }

        file << password << "\n";

        cout << "\r[POISON] ~ Progresso: " << number + 1 << " de " << max_case + 1 << " (" << fixed << setprecision(2) << (double)number / max_case * 100.0 << "%)";
    }

    cout << "\n\n[POISON] ~ Arquivo gerado com sucesso! (wifi-wordlist.txt)" << endl;
    cout << "[POISON] ~ Pressione ENTER ou qualquer tecla para sair.";

    cin.ignore();

    return 0;
}