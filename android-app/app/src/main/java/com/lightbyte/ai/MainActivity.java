package com.lightbyte.ai;

import android.os.Bundle;
import android.view.Gravity;
import android.view.ViewGroup;
import android.graphics.Color;
import android.widget.*;
import androidx.appcompat.app.AppCompatActivity;
import com.google.android.material.button.MaterialButton;
import com.google.android.material.textfield.TextInputEditText;

public class MainActivity extends AppCompatActivity {

    private LinearLayout messages;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(20, 20, 20, 12);
        root.setBackgroundColor(Color.rgb(17, 19, 24));

        TextView title = new TextView(this);
        title.setText("✦ LIGHT BYTE");
        title.setTextSize(25);
        title.setTextColor(Color.rgb(255, 138, 80));
        title.setGravity(Gravity.CENTER_VERTICAL);
        title.setPadding(8, 12, 8, 20);
        root.addView(title);

        TextView welcome = new TextView(this);
        welcome.setText("Твой интеллектуальный помощник");
        welcome.setTextSize(17);
        welcome.setTextColor(Color.WHITE);
        welcome.setPadding(8, 12, 8, 18);
        root.addView(welcome);

        ScrollView scroll = new ScrollView(this);
        messages = new LinearLayout(this);
        messages.setOrientation(LinearLayout.VERTICAL);
        scroll.addView(messages);

        root.addView(scroll, new LinearLayout.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT, 0, 1
        ));

        TextInputEditText input = new TextInputEditText(this);
        input.setHint("Напиши сообщение...");
        input.setTextColor(Color.WHITE);
        input.setHintTextColor(Color.GRAY);
        input.setSingleLine(false);

        MaterialButton send = new MaterialButton(this);
        send.setText("Отправить");

        LinearLayout bottom = new LinearLayout(this);
        bottom.setOrientation(LinearLayout.VERTICAL);
        bottom.addView(input);
        bottom.addView(send);

        root.addView(bottom);
        setContentView(root);

        addMessage("LIGHT BYTE", "Привет! Я готов помочь тебе.");
        send.setOnClickListener(v -> {
            String text = input.getText() == null ? "" :
                input.getText().toString().trim();

            if (!text.isEmpty()) {
                addMessage("Ты", text);
                input.setText("");
                addMessage("LIGHT BYTE", "Интерфейс готов. Подключение ИИ добавим следующим этапом.");
            }
        });
    }

    private void addMessage(String author, String text) {
        TextView message = new TextView(this);
        message.setText(author + "\n" + text);
        message.setTextSize(15);
        message.setTextColor(Color.WHITE);
        message.setBackgroundColor(Color.rgb(38, 41, 49));
        message.setPadding(16, 14, 16, 14);

        LinearLayout.LayoutParams params = new LinearLayout.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT,
            ViewGroup.LayoutParams.WRAP_CONTENT
        );
        params.setMargins(0, 6, 0, 6);
        messages.addView(message, params);
    }
}
