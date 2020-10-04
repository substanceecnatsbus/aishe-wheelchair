package com.example.wheelchairmonitoringapp.ui.main;

import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.fragment.app.Fragment;

import com.example.wheelchairmonitoringapp.R;
import com.github.mikephil.charting.charts.LineChart;
import com.github.mikephil.charting.components.XAxis;
import com.github.mikephil.charting.data.Entry;
import com.github.mikephil.charting.data.LineData;
import com.github.mikephil.charting.data.LineDataSet;
import com.github.mikephil.charting.interfaces.datasets.ILineDataSet;

import java.net.URISyntaxException;
import java.util.ArrayList;
import java.util.Random;
import java.util.Timer;
import java.util.TimerTask;

import io.socket.client.IO;
import io.socket.client.Socket;
import io.socket.emitter.Emitter;

public class RealTimeECGFragment extends Fragment {
    public static final String TAG = "RealTimeECGFragment";

    private LineChart lineChart;

    private int addIndex = 0, removeIndex = 0;

    private Socket socket;
    {
        String ServerURL = "http://192.168.137.1:3000/socket/ecg";
        try {
            socket = IO.socket(ServerURL);
            socket.on(Socket.EVENT_CONNECT, new Emitter.Listener() {

                @Override
                public void call(Object... args) {
                    Log.d(TAG, "Socket Connected");
                }

            }).on("mobile-ecg", new Emitter.Listener() {

                @Override
                public void call(final Object... args) {
                    //Log.d(TAG, args[0].toString());
                    final float value = Float.parseFloat(args[0].toString().split(",")[1]);

                    new Handler(Looper.getMainLooper()).post(new Runnable() {
                        @Override
                        public void run() {
                            LineData ld = lineChart.getLineData();

                            if(ld.getEntryCount() > 150) {
                                ld.removeEntry(0, 0);
                                lineChart.notifyDataSetChanged();
                                lineChart.invalidate();
                            }

                            Entry e = new Entry(addIndex, value);
                            ld.addEntry(e, 0);
                            addIndex++;



                            lineChart.notifyDataSetChanged();
                            lineChart.invalidate();
                        }
                    });

                }

            }).on(Socket.EVENT_DISCONNECT, new Emitter.Listener() {
                //TODO: Clear the graph, reset ulit pag nag recon

                @Override
                public void call(Object... args) {
                    Log.d(TAG, "Socket Disconnected");
                }
            });
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
    }

    @Override
    public View onCreateView(
            @NonNull LayoutInflater inflater, ViewGroup container,
            Bundle savedInstanceState) {
        View root = inflater.inflate(R.layout.fragment_chart, container, false);
        final TextView textView = root.findViewById(R.id.textView);
        textView.setText("Tite");
        return root;
    }

    @Override
    public void onViewCreated(@NonNull View view, @Nullable Bundle savedInstanceState) {
        super.onViewCreated(view, savedInstanceState);
        Log.d(TAG, "View Created");
        lineChart = view.findViewById(R.id.chart);
        lineChart.setTouchEnabled(true);
        lineChart.setPinchZoom(true);
        lineChart.getAxisLeft().setDrawGridLines(false);
        lineChart.getXAxis().setDrawGridLines(false);
        lineChart.getXAxis().setPosition(XAxis.XAxisPosition.BOTTOM);
        lineChart.getAxisRight().setDrawGridLines(false);;
        lineChart.getAxisRight().setDrawLabels(false);


        ArrayList<Entry> values = new ArrayList<>();

        LineDataSet dataSet = new LineDataSet(values, "ECG ng tite mo");
        dataSet.setDrawValues(false);
        dataSet.setDrawCircles(false);

        ArrayList<ILineDataSet> dataSets = new ArrayList<>();
        dataSets.add(dataSet);

        final LineData data = new LineData(dataSets);
        lineChart.setData(data);
        lineChart.invalidate();

//        new Timer().scheduleAtFixedRate(new TimerTask(){
//            @Override
//            public void run(){
//                new Handler(Looper.getMainLooper()).post(new Runnable() {
//                    @Override
//                    public void run() {
//                        Log.d("UI thread", "I am the UI thread");
//                        Random rand = new Random();
//                        LineData ld = lineChart.getLineData();
//
//                        Entry e = new Entry(ld.getEntryCount() + 1, rand.nextInt(100));
//                        ld.addEntry(e, 0);
//
//                        lineChart.notifyDataSetChanged();
//                        lineChart.invalidate();
//                    }
//                });
//            }
//        },0,1000);


        socket.connect();
    }
}
